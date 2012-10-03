from google.appengine.ext import db
from urlparse import urlparse as urlp
import os.path

class ImportedList(db.Model):
  ctime = db.DateTimeProperty(auto_now = True, auto_now_add = True)#verbose_name = 'Time created', )

class Hit(db.Model):
  path = db.StringProperty()#verbose_name = 'The request made')
  comment = db.StringProperty()#verbose_name = 'If a metalink is hit, this is the url'
  referer = db.StringProperty()#verbose_name = 'The referer set in the request')
  remote_addr = db.StringProperty()#vebose_name = 'IP of host that made the request')
  ctime = db.DateTimeProperty(auto_now_add = True)#, verbose_name = 'Date and time at which the connection was made')
  
class File(db.Model):
  scheme = db.StringProperty() #	0 	URL scheme specifier 	empty string
  hostname = db.StringProperty() #	1 	hostname part 	empty string (Takes the netloc part into account, but scheme dictates port)
  path = db.StringProperty() 	#2 	Hierarchical path 	empty string
  #IGNORED params = db.StringProperty() #	3 	Parameters for last path element 	empty string
  #IGNORED query = db.StringProperty() #	4 	Query component 	empty string
  #IGNORED fragment 	5 	Fragment identifier 	empty string

  name = db.StringProperty()
  name_lower = db.StringProperty()
  mime_type = db.StringProperty(default = '')#, verbose_name = 'MIME type')
  size = db.IntegerProperty(default = 0)#, verbose_name = 'Size of the file in bytes')
  
  #Digests
  md5 = db.StringProperty()
  sha1 = db.StringProperty()
  sha256 = db.StringProperty()
  sha512 = db.StringProperty()
  
  #Validation and general book-keeping  
  #valid = db.BooleanProperty(default = False)
  available = db.BooleanProperty(default = False)
  mtime = db.DateTimeProperty(auto_now = True)#verbose_name = 'Modification time', )

  def largest_hash(self):
    if self.sha512:
      return self.sha512
    if self.sha256:
      return self.sha256
    if self.sha1:
      return self.sha1
    if self.md5:
      return self.md5

  def digests(self):
    #Return digests as a dictionary
    d = {}
    if self.sha512:
      d['sha512'] = self.sha512
    if self.sha256:
      d['sha256'] = self.sha256
    if self.sha1:
      d['sha1'] = self.sha1
    if self.md5:
      d['md5'] = self.md5
    return d

  def set_url(self, url):
    #if self.key() != url.geturl():
    #  raise Exception('Trying to set url for invalid url key, key=%s url=%s' % (self.key(), url.geturl()))
    #Sanity check
    if hasattr(url, 'geturl'):
      url = File.urlparse(url.geturl())
    else:
      url = File.urlparse(url)
    self.scheme = url.scheme # 	0 	URL scheme specifier 	empty string
    self.hostname = url.hostname #	1 	Network location part 	empty string
    self.path = url.path# 	2 	Hierarchical path 	empty string
    self.name = os.path.basename(url.path)
    self.name_lower = self.name.lower()

  def url(self):
    return '%s://%s%s' % (self.scheme, self.hostname, self.path)

  @staticmethod
  def urlparse(url):
    url = urlp(url)
    
    #Sanity checks:
    if url.scheme == None or len(url.scheme) == 0:
      raise Exception('Empty scheme in url')
    if url.hostname == None or len(url.hostname) == 0:
      raise Exception('Empty hostname in url')
    if url.path == None or len(url.path) == 0:
      raise Exception('Empty path in url')

    #Sanitize url      
    return urlp(
      '%s://%s%s' %
        (
          url.scheme,
          url.hostname,
          url.path
        ))


