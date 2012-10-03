#!/usr/bin/env python
from google.appengine.ext import webapp
import util
from models import File, ImportedList, Hit
from urlparse import urlparse
import re
from google.appengine.api import urlfetch
from insert_parser import insert_files_from, hash_sizes, lower_hex_regex 
import os.path
import datetime

BOT_REFERER = 'http://www.dynmirror.net/'

def search(query, offset = 0, limit = 10):
  results = None
  search_type = None

  if query:
    if len(query) > 10 and lower_hex_regex.match(query):
      for d in hash_sizes:
        if len(query) == hash_sizes[d]:
          search_type = '%s search' % d.upper()
          results = File.all().filter('%s =' % d, query)
          break
      if not search_type:
        search_type = 'SHA1 prefix search'
        results = File.all().filter('sha1 >= ', query).filter('sha1 < ', query + u'\ufffd')
    else: #Last resort: basename matching
      match_case = 0
      if query.lower() == query:
        results = File.all().filter('name_lower >= ', query).filter('name_lower < ', query + u'\ufffd')
      else:
        match_case = 1
        results = File.all().filter('name >= ', query).filter('name < ', query + u'\ufffd')
      search_type = 'Filename prefix search%s' % ['', ', matching case,'][match_case]
      #db.GqlQuery("SELECT * FROM MyModel WHERE prop >= :1 AND prop < :2", "abc", u"abc" + u"\ufffd")
  if results and limit:
    results.fetch(limit)
  return {'results': results, 'search_type': search_type, 'query': query, 'search_limit': limit, 'search_offset': offset}

class Home(webapp.RequestHandler, util.TemplateRendering):
  def head(self):
    return
  def get(self):
    query = self.request.get('q')
    if query:
      return self.render_to_response('home.html', search(query))
    #path == /metalink/ comment == link
    last = []
    referers = []
    for l in Hit.all().filter('path =', '/metalink/').order('-ctime').fetch(20):
      if not last.count(l.comment):
        last.append(l.comment)
      r = l.referer.strip('/')
      if r and not referers.count(r):
        referers.append(r)
    return self.render_to_response('home.html', {'last_metalinks': last, 'last_referrers': referers})

class Template(webapp.RequestHandler, util.TemplateRendering):
  def head(self):
    return
  def get(self):
    tname = os.path.dirname(self.request.path.replace('.', '')) + '.html'
    bookmarklet = file('templates/bookmarklet.js').read().replace('\n', '').replace(' ', '').replace('_',' ')
    return self.render_to_response(tname, {'bookmarklet': bookmarklet})
  
class Search(webapp.RequestHandler, util.TemplateRendering):
  def get(self):
    self.post()
  def post(self):
    self.response.headers['Content-Type'] = 'application/xhtml+xml'
    query = self.request.get('q')
    r = search(query)
    return self.render_to_response('results.xml', r)


#Use HEAD to verify the files and their length

class Add(webapp.RequestHandler, util.TemplateRendering):
  def head(self):
    return
  def get(self):
    url = self.request.get('url')
    msgs = []
    if len(url):
      parsed_url = None
      try:
        parsed_url = File.urlparse(url)
      except Exception, e:
        msgs.append(('bad', 'Could not parse "%s" into a valid url' % url))
      if parsed_url:
        msgs.append(('normal', 'Trying to download "%s"' % parsed_url.geturl()))
        try:
          if parsed_url.hostname == 'localhost' or parsed_url.hostname.endswith('.lan'):
            raise Exception('Local network address requested.')
          if re.match(r'[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', parsed_url.hostname) or parsed_url.hostname.count('['):
            raise Exception('IPv4/IPv6 literal addresses are not supported')
          if parsed_url.hostname.count('.in-addr.arpa') or parsed_url.hostname.count('.ipv6-literal.net'):
            raise Exception('Found illegal ".in-addre.arpa" or ".ipv6-literal.net" in hostname')
          
          #Keep from doing an url in the ImportedList
          url = parsed_url.geturl()
          done = ImportedList.get_by_key_name(url)
          if done:
            msgs.append(('normal', 'This download is still in our "already done" list, but thank you for reporting it.'))
            raise Exception('Already checked in the last week.')

          
          result = urlfetch.fetch(url)
          if result.status_code == 200:
            ImportedList.get_or_insert(url)
            #Parse the content
            path = os.path.dirname(url)
            msgs.extend(insert_files_from(path, result.content))
            return self.render_to_response('add.html', {'url': parsed_url.geturl(), 'msgs': msgs})
          msgs.append(('bad', 'Download failed with status code %i' % result.status_code))
        except Exception, e:
          msgs.append(('bad', 'Download failed: %s' % str(e)))
          pass
         
    self.render_to_response('add.html', {'url': url, 'msgs': msgs})

class Stats(webapp.RequestHandler, util.TemplateRendering):
  def head(self):
    return
  def get(self):
    limit = 20
    return self.render_to_response('stats.html', {'limit': limit, 'files': File.all().order('-mtime').fetch(limit)})
    
class Latest(webapp.RequestHandler, util.TemplateRendering):
  def head(self):
    return
  def get(self):
    limit = 20
    return self.render_to_response('latest.html', {'limit': limit, 'files': File.all().order('-mtime').fetch(limit)})

class RobotsTXT(webapp.RequestHandler):
  def head(self):
    return
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'  
    self.response.out.write('# 200 OK')

class Validate(webapp.RequestHandler, util.TemplateRendering):
  def head(self):
    self.not_found();
    return
  def get(self):
    #TODO insert admin logs
    #self.response.headers['Content-Type'] = 'text/plain'  
    #Validate with url-fetch head on a few urls
    for f in File.all().filter('available = ', False).fetch(1):
      response = None
      #self.response.out.write('URL: %s\n' % f.url())
      try:
        response = urlfetch.fetch(f.url(), method = urlfetch.HEAD)#, headers = {'Referer': BOT_REFERER})
      except Exception, e:
        f.delete()
        #self.response.out.write('DEL: %s\n' % str(e))
        continue
      #Check response data
      if not response.status_code == 200:
        f.delete()
        #self.response.out.write('DEL: status %i\n' % response.status_code)
        continue
      #self.response.out.write(str(dir(response)))
      #Read content-MD5/SHA1 etc.
      #Content-Length, Content-MD5
      try:
        f.size = int(response.headers['content-length'])
        f.mime_type = response.headers['content-type']
        #TODO Add support for http://www.ietf.org/rfc/rfc1864.txt MD5 as base64 encoded digest
        #md = response.headers['content-md5'].lower()
        #if len(md) == 32:
        #  f.md5 = md
      except Exception:
        pass
      f.available = True
      f.put()

class Janitor(webapp.RequestHandler, util.TemplateRendering):
  def head(self):
    self.not_found();
    return
  def get(self):
    #Clean up Imported List
    [f.delete() for f in ImportedList.all().filter('ctime < ', datetime.datetime.now() - datetime.timedelta(days = 7))]
    
    #Clean up Hit List
    #TODO rewrite to make sure we always have a few redirects left
    hitCount = Hit.all().count()
    if hitCount > 30:
      [f.delete() for f in Hit.all().filter('ctime < ', datetime.datetime.now() - datetime.timedelta(days = 30))]

    #Remove old files
    for f in File.all().filter('available = ', True).filter('mtime < ', datetime.datetime.now() - datetime.timedelta(days = 32)).fetch(100):
      f.available = False
      f.put()
