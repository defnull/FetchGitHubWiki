#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import re
import sys
import os.path
from bottle import SimpleTemplate

USER = sys.argv[1]
PROJECT = sys.argv[2]
DOCDIR = len(sys.argv) > 3 and os.path.abspath(sys.argv[3]) or os.path.abspath('.')
TEMPLATE = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd" >
<html>
  <head>
    <title>{{title.title()}} - Bottle Dokumentation</title>
    <style  type="text/css">
      h1 {border-bottom: 5px solid #ddd;}
      pre {
        background: #eee;
        border: 1px dashed #ddd;
        padding: 0 1em;
        margin: 1em 10em 1em 1em;
      }
      #navigation {
        float: right;
        border: 1px solid #ddd;
        border-width: 0 0 1px 1px;
        background: #fff;
        padding: 1em;
        margin-left: 1em;
      }
    </style>
  </head>
<body>
  <div id='navigation'>
    <h3>Navigation</h3>
    <ul>
    %for p in pages:
      <li><a href='./{{p}}.html'>{{p.title()}}</a></li>
    %end
    </ul>
  </div>
  {{html}}
</body>
'''


def main():
    print "GitHub User:", USER
    print "GitHub Project:", PROJECT
    print "Target directory:", DOCDIR
    pages = fetch_pagenames(USER, PROJECT)
    if not pages:
        print "ERROR: Invalid user or project name."
        return 1
    print "Pages:", ', '.join(pages)

    tpl = SimpleTemplate(TEMPLATE)
    for page in pages:
        fn = '%s/%s.html' % (DOCDIR, page.lower())
        print "Fetching", page.title(), "-->", fn
        raw = '\n'.join(fetch_page(USER, PROJECT, page))
        raw = re.sub(r'http://wiki.github.com/%s/%s/(\w+)' % (USER, PROJECT), './\\1.html', raw)
        if raw.strip():
            try:
                fp = open(fn, 'w')
                fp.write(tpl.render(title=page.title(), html=raw, pages=pages))
                fp.close()
            except IOError:
                print "ERROR: Could not save file (IOError)"
        else:
            print "ERROR: Empty page or download error."
    return 0


def fetch_pagenames(user, project):
    """ Returns a list of all pagenames of a github wiki """
    try:
        raw = urllib2.urlopen("http://wiki.github.com/%s/%s" % (user, project)).read()
    except:
        return []
    pages = set(['home'])
    for m in re.findall(r"http://wiki\.github\.com/%s/%s/(\w+)\"" % (user, project), raw):
        pages.add(m)
    return list(pages)


def fetch_page(user, project, pagename):
    """ Yield the content of a github wiki page (without newlines)"""
    try:
        raw = urllib2.urlopen("http://wiki.github.com/%s/%s/%s" % (user, project, pagename)).read()
    except:
        raw = ''
    consume = False
    for line in raw.splitlines():
        if '<h1>' in line:
            consume = True
            yield '<div class="main">'
            yield line
        elif consume:
            if '<!-- sidebar -->' in line:
                break
            elif len(line.strip()):
                yield line

if __name__ == "__main__":
    sys.exit(main())
