#!/usr/bin/env python
import re
from models import File
import os.path
#http://mirror-fpt-telecom.fpt.net/gcc/releases/gcc-3.2.2/md5.sum
#ftp://ftp.freebsd.org/pub/FreeBSD/releases/amd64/ISO-IMAGES/7.2/CHECKSUM.MD5
#ftp://ftp.freebsd.org/pub/FreeBSD/releases/amd64/ISO-IMAGES/7.2/CHECKSUM.SHA256
#http://opensolaris.fastbull.org/2008/05/md5sums.txt WEIRD
#http://mirror-fpt-telecom.fpt.net/kde/Attic/3.5.4/src/MD5SUMS

lower_hex_regex = re.compile(r'^[a-f0-9]+$')

hash_sizes = {
  'md5': 32,
  'sha1': 40,
  'sha256': 64,
  'sha512': 128,

  32: 'md5',
  40: 'sha1',
  64: 'sha256',
  128: 'sha512',

  }

def insert_file(path, fname, digest_type, digest):
  url = File.urlparse(os.path.join(path, fname))
  f = File.get_or_insert(url.geturl())
  f.set_url(url)
  exec 'f.%s = digest' % digest_type
  f.put()
  
def insert_files_from(path, content):
  #Init regex if needed
  re_digest = re.compile(r'^\s*([a-fA-F0-9]{32}|[a-fA-F0-9]{40}|[a-fA-F0-9]{64}|[a-fA-F0-9]{128})\s+\*?(\S+)\s*$', re.MULTILINE)
  re_digest_open = re.compile(r'^\s*(MD5|SHA1|SHA256|SHA512)\s?\((.+?)\) ?= ?([a-fA-F0-9]{32}|[a-fA-F0-9]{40}|[a-fA-F0-9]{64}|[a-fA-F0-9]{128})\s*$', re.MULTILINE)


  #Return a set of messages with information on what got inserted and what not
  msgs = [('normal', 'Searching for files relative to %s' % path)]
  for m in re_digest.finditer(content):
    digest = m.group(1).lower()
    digest_type = hash_sizes[len(digest)]
    name = os.path.normpath(m.group(2))
    if name.startswith('..'):
      #TODO Normalize path before testing on this simple '..', this is NOT secure enough
      msgs.append(('bad', 'Skipping %s for security reasons: it is a relative path going up.' % name))
      continue
    insert_file(path, name, digest_type, digest)
    msgs.append(('insert', 'Inserted %s(%s) = %s' % (digest_type, name, digest)))
  for m in re_digest_open.finditer(content):
    digest = m.group(3).lower()
    digest_type = m.group(1).lower()
    name = os.path.normpath(m.group(2))
    if name.startswith('..'):
      #TODO Normalize path before testing on this simple '..', this is NOT secure enough
      msgs.append(('bad', 'Skipping %s for security reasons: it is a relative path going up.' % name))
      continue
    insert_file(path, name, digest_type, digest)
    msgs.append(('insert', 'Inserted %s(%s) = %s' % (digest_type, name, digest)))
  if len(msgs) == 1:
    msgs = [('bad', 'Reached end of file without finding any file digests')]
  return msgs
