var _as = document.getElementsByTagName("a"),
  metainfo = RegExp('https?://.*(\.(md5|sha(1|256|512))(sums?)?|/(MD5|SHA(1|256|512))(SUM)?S?)$', 'i'),
  i = 0;
for (i = 0; i < as.length ; i++)
{
  if(metainfo.test(as[i].href))
    window.open('http://www.dynmirror.net/add/?url=' + escape(as[i].href)); /* MAKE AJAX CALLS! */
  if(as[i].href.indexOf('http') == 0 && as[i].href.lastIndexOf('/') != as[i].href.length -1)
  {
    as[i].href = 'http://www.dynmirror.net/metalink/?url=' + as[i].href;
    as[i].innerHTML = "<sup>DM</sup>" + as[i].innerHTML;
  }
}
