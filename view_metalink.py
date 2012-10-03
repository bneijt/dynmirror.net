from google.appengine.ext import webapp
from models import File, Hit
import util
import re
import os.path
import datetime
import random
import urlparse
from insert_parser import insert_files_from, hash_sizes, lower_hex_regex 

#Country domains: ac ad ae af ag ai al am an ao aq ar as at au aw ax az ba bb bd be bf bg bh bi bj bm bn bo br bs bt bv bw by bz ca cc cd cf cg ch ci ck cl cm cn co cr cu cv cx cy cz de dj dk dm do dz ec ee eg eh er es et eu fi fj fk fm fo fr ga gb gd ge gf gg gh gi gl gm gn gp gq gr gs gt gu gw gy hk hm hn hr ht hu id ie il im in io iq ir is it je jm jo jp ke kg kh ki km kn kp kr kw ky kz la lb lc li lk lr ls lt lu lv ly ma mc md me mg mh mk ml mm mn mo mp mq mr ms mt mu mv mw mx my mz na nc ne nf ng ni nl no np nr nu nz om pa pe pf pg ph pk pl pm pn pr ps pt pw py qa re ro rs ru rw sa sb sc sd se sg sh si sj sk sl sm sn so sr st su sv sy sz tc td tf tg th tj tk tl tm tn to tp tr tt tv tw tz ua ug uk um us uy uz va vc ve vg vi vn vu wf ws ye yt yu za zm zw 


class LinkElement:
  def __init__(self):
    self.urls = []
    self.name = ''
    self.digests = {}
    self.scheme = ''
    self.size = 0
  

class Metalink(webapp.RequestHandler, util.TemplateRendering):
  def post(self):
    self.get()
  def head(self):
    self.response.headers['Content-Type'] = 'application/metalink+xml'
    return
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    devhelp_url = '\n\nPlease visit http://www.dynmirror.net/help/developers/ for more information.'
    #If url is given, use that as the digest
    digest = os.path.basename(self.request.path)
    if len(digest) and not digest.endswith('.metalink'):
      return self.not_found('404 not found: If you do file look-ups by digest, it needs to end in ".metalink".' + devhelp_url)
    digest = digest[:-len('.metalink')]
    digests = {}
    url = self.request.get('url')
    fileLink = LinkElement()
    
    if len(url):
      #Try to load the digest from the database
      url = File.urlparse(url).geturl()
      
      #Add Coral link if wanted
      if self.request.get('coral', default_value = 'not_set') != 'not_set':
        cu = urlparse.urlparse(url) #Parse for the coral url
        if cu.scheme == 'http' and not cu.netloc.endswith('.nyud.net'):
          fileLink.urls.append({'v': 'http://' + cu.hostname + '.nyud.net' + cu.path, 'a':{'type': File.urlparse(url).scheme}})
      Hit(path = self.request.path, remote_addr = self.request.remote_addr, referer = self.request.headers.get('referer', ''), comment = url).save()
      f = File.get_by_key_name(url)
      if f == None:
        #Host a link only metalink
        fileLink.name = os.path.basename(url)
        fileLink.urls.insert(0, {'v': url, 'a':{'type': File.urlparse(url).scheme}})
        self.response.headers['Content-Type'] = 'application/metalink+xml'
        self.response.headers['Content-Disposition'] = 'attachment; filename="%s.metalink"' % os.path.basename(url).replace('"', '\\"')
        return self.render_to_response('metalink.xml', {'files': [fileLink], 'comment': 'Link only, because no validated link information could be found in the database. Make sure you use the _exact_ url you used to add the metadata.'})
      #inherit all the digest information from the file in db
      fileLink.name = f.name
      fileLink.size = f.size
      fileLink.digests.update(f.digests())
      if len(digest) > 0:
        return self.response.out.write('For security reasons, you can not combine digest and url, because we can not determine which is authorative and what to do in case they do not match in the database.' + devhelp_url)
    
    if len(digest) > 0:
      #Malformed digest
      if not hash_sizes.has_key(len(digest)):
        return self.not_found('404 Not Found, the digest is considered malformed. Make sure it is lowercase hex representing an MD5, SHA1, SHA256 or SHA512.' + devhelp_url)
      if not lower_hex_regex.match(digest):
        return self.not_found('404 Not Found, the digest is considered malformed because it did not match /[0-9a-f]/.' + devhelp_url)
      #OK, so a digest is given, set the digest in the fileLink to the given value
      fileLink.digests[hash_sizes[len(digest)]] = digest
    
    #TODO Unique hosts; hosts = set
    #Explode the file using all known digests, both url and digest
    names = {}
    sizes = {}
    cntry_regex = re.compile('.*\.(a[cdefgilmnoqrstuwxz]|c[acdfghiklmnoruvxyz]|b[abdefghijmnorstvwyz]|e[ceghrstu]|d[ejkmoz]|g[abdefghilmnpqrstuwy]|f[ijkmor]|i[delmnoqrst]|h[kmnrtu]|k[eghimnprwyz]|j[emop]|m[acdeghklmnopqrstuvwxyz]|l[abcikrstuvy]|o[m]|n[acefgilopruz]|q[a]|p[aefghklmnrstwy]|s[abcdeghijklmnortuvyz]|r[eosuw]|u[agkmsyz]|t[cdfghjklmnoprtvwz]|w[fs]|v[aceginu]|y[etu]|z[amw])$')
    for digest_type in fileLink.digests:
      files = File.all().filter('%s = ' % digest_type, fileLink.digests[digest_type]).fetch(20)
      for f in files:
        attr = {'type': 'http'}#Optimization, currently only HTTP supported f.scheme
        cntry = cntry_regex.match(f.hostname)
        if cntry:
          attr['location'] = cntry.group(1)
        fileLink.urls.append({'v': f.url(), 'a': attr})
        names.setdefault(f.name, 0)
        names[f.name] += 1
        sizes.setdefault(f.size, 0)
        sizes[f.size] += 1
    
    #If a name is given, just rename the file
    name = self.request.get('name')
    if name:
      fileLink.name = name
    if not fileLink.name:
      #Democratic naming
      names = [(names[k], k) for k in names]
      names.sort()
      fileLink.name = names[-1][1]
    if not fileLink.size:
      #Democratic size
      sizes[0] = 0
      sizes = [(sizes[k], k) for k in sizes]
      sizes.sort()
      fileLink.size = sizes[-1][1]
    random.shuffle(fileLink.urls)      
    self.response.headers['Content-Type'] = 'application/metalink+xml'
    self.response.headers['Content-Disposition'] = 'attachment; filename="%s.metalink"' % os.path.basename(fileLink.name).replace('"', '\\"')
    return self.render_to_response('metalink.xml', {'files': [fileLink]})

