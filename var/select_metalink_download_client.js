
function array_contains(a, e) {
	for(j=0;j<a.length;j++)
	  if(a[j]==e)
	    return true;
	return false;
}

function subsetBy(clients, keyword)
{

  var subset = [],
    i = 0, cidx = 0;
  for(i = 0; i < clients.length; ++i)
  {
    for(cidx = 0; cidx < clients[i][2].length; ++cidx)
    {
      if(clients[i][2][cidx][0] == '!')//Special negation keyword
        continue;
      //Prefix search for client keyword in keywords
      if(keyword.indexOf(clients[i][2][cidx]) == 0)
      {
        subset.push(clients[i]);
      }
    }
  }
  return subset;
}
function generateKeywords()
{
  //Find keywords based on platform, browser etc.
  var ua = navigator.userAgent.replace(/[)(;]/g,' ');
  ua = ua.replace(/ +/g, ' ')
  var keywords = ua.split(' ');
  //Example: Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20090902 Ubuntu/9.10 (karmic) Firefox/3.5.3
  return keywords;
}
function clientHTML(client)
{
  return '<div class="client" onclick="window.location = \''+client[1]+'\';"><p><h3>'+client[0]+'</h3>'+client[3] + '<div class="morelink"><a href="'+client[1]+'">more information &rarr;</a></div></div>';
}
function proposedClients()
{
  //Start with a list of all clients
  //keywords used are: 'Windows', 'Linux', 'Mac', 'Firefox', 'MSIE', 'Opera'
  var clients = [
    ['Orbit Downloader', 'http://www.orbitdownloader.com/', ['Windows', 'Firefox', 'MSIE', 'Opera'],
      'Orbit Downloader is a download client that integrates with all mayor browsers on the Windows platform. It is freeware and there is no commercial support option.'],
    ['DownloadThemAll Firefox Extension', 'http://www.downthemall.net/', ['Linux', 'Windows', 'Mac', 'Firefox'],
      'DownThemAll (or just dTa) is a powerful yet easy-to-use Mozilla Firefox extension that adds new advanced download capabilities to your browser. It has basic Metalink support since version 1.0. Download the metalink file like normal and after the download, DownloadThemAll will show a dialog allwing you to select and download the things you want.'],
    ['GetRight', 'http://getright.com/', ['Windows', 'Firefox', 'MSIE', 'Opera'],
      'GetRight is a Windows download client. You can get a free trial, but for a full experience you need to buy a license.'],
    ['KGet', 'http://www.kde.org/', ['Linux', 'Firefox', 'MSIE', 'Opera'],
      "KDE's native download manager, supports Metalink since KDE 4. If you have KDE running."],
    ['Aria2', 'http://aria2.sourceforge.net/', ['Linux', 'Firefox', 'MSIE', 'Opera'],
      'Aria 2 is a commandline downloader for GNU/Linux. It can be found in most repositories and is known for speed and efficiency. You can also find GUI front-ends for various environments though their project homepage.'],
    ['wxDownload Fast', 'http://dfast.sourceforge.net/', ['Windows', 'Linux', 'Mac', 'Firefox', 'MSIE'],
      'wxDownload Fast (also known as wxDFast) is an open source download manager. It is multi-platform and builds on Windows(2k,XP), Linux and Mac OS X(binary still not available). Besides that, it is a multi-threaded download manager. This means that it can split a file into several pieces and download the pieces simultaneously. Created in C++ using the wxWidgets(wxWindows) library.'],
    ['Phex', 'http://www.phex.org/', ['Windows', 'Linux', 'Mac', 'Firefox', 'MSIE'],
      'Phex is a P2P download clients with support for Metalinks. You can use Phex to import a metalink. Phex is written in Java and runs on Windows, MacOSX and GNU/Linux, as well as on every other plattform which supports a Java VM. '],
/*
    ['', '', [],
      ''],
    ['', '', [],
      ''],
*/
    ],
    keywords = generateKeywords(),
    i = 0,
    used_keywords = [];
  //Find platform and other keywords
  
  //While we can still specialize without no suggestions, make a subset selection
  for(i = 0; i < keywords.length; ++i)
  {
    var subset = subsetBy(clients, keywords[i]);
    if(subset.length)
    {
      clients = subset;
      if(!array_contains(used_keywords, keywords[i]))
        used_keywords.push(keywords[i]);
    }
  }
  var s = $.map(clients, clientHTML);
  s.splice(0,0, ['<p>We have made a selection for you based upon the following keywords: '+$('<div/>').text(used_keywords.join(', ')).html()+'']);
  return s.join('\n');
}

$('#client_suggestions').html(proposedClients());
