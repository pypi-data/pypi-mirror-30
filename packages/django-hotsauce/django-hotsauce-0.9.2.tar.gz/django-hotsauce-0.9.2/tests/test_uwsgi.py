#!/usr/bin/env python
import urllib
import demjson

url = 'http://localhost:9001'

fp = urllib.urlopen(url)
json = demjson.decode(fp.read())

connections = 0

for worker in json['workers']:
    connections += worker['requests']

print connections


