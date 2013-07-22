#!/usr/bin/env python
import sys
import requests
import scraperwiki
     
URL = "http://en.wikipedia.org/w/api.php?action=query&list=allimages&aiprop=url|user|timestamp|size|mime&ailimit=100&format=json&aifrom=%s"
     
data = requests.get(URL % sys.argv[1]).json()
images = data['query']['allimages']
scraperwiki.sqlite.save(['name'], images, 'images')
