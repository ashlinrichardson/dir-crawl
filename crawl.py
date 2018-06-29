#!/usr/bin/env python
'''20171117 Doesn't explicitly extract hierarchy info re: org. units
20180213 it should'''
import os
import re
import sys
import pickle
import urllib2
import datetime
from HTMLParser import HTMLParser


def pad(s, n):  # pad from left with 0's to fixed length
    s = str(s)
    while len(s) < n:
        s = '0' + s
    return s

# assume not run multiple times per jour
t = datetime.date.today()
dat_f = pad(t.year, 4) + pad(t.month, 2) + pad(t.day, 2) + '_dat'

file_sep = "\\"
if os.name != 'nt':
    file_sep = "/"

if not os.path.exists(dat_f):
    os.mkdir(dat_f)

dat_f = dat_f + file_sep

url_to_id = {}  # assign a file-id to a given URL
id_to_url = {}  # reverse lookup
id_to_data = {}  # saving all data in one file might not work, but we'll try
next_id = 0  # assign index to each URL

visited = []  # list of URL's visited
to_visit = []  # list of URL's to visit


def incr(c):  # encoding functions to obfuscate address
    return chr(ord(c) + 1)


def decr(c):
    return chr(ord(c) - 1)


def enc(s):
    r = list(s)
    for i in range(0, len(r)):
        r[i] = incr(r[i])
    return "".join(r)


def dec(s):
    r = list(s)
    for i in range(0, len(r)):
        r[i] = decr(r[i])
    return "".join(r)

root = dec('iuuq;00ejs/hpw/cd/db')
bs = dec('0huet/dhj')
hier = dec('@Joefy>CzVojuIjfs')
startpath = dec('0huet/dhj') + hier
start = root + startpath

# unobfuscated addresses
print "basepath", root
print "script", bs
print "startloc", hier
print "startstem", startpath
print "startpath", start


''' fetch data from a given URL, if we've not yet done so this run..
..inevitably, pages are listed more than once, so this code avoids
downloading the same thing more than once by returning the saved copy'''

def wget(url):
    if url in url_to_id:
        my_id = url_to_id[url]
        return id_to_data[my_id]
    else:
        print "\t\t", ("open('" + url + "')")
        response = urllib2.urlopen(url)  # print response.info()
        html = response.read().strip()
        return html

''' add a URL to the database, assigning an ID ("take a number" when getting drivers
license renewed.. add() gets called every time we "discover" a URL (that we want to visit
"later")'''


def add(url):
    global to_visit, visited, next_id, url_to_id
    # add a url to "the" database
    if url not in url_to_id:
        data = wget(url)
        url_to_id[url], id_to_url[next_id], id_to_data[next_id] = \
            next_id, url, data

        # save the URL in a file
        open(dat_f + str(next_id)+"_u.txt", "wb").write(url)

        # save the retrieved data at a file
        open(dat_f + str(next_id)+"_d.txt", "wb").write(data)

        next_id += 1
        if url in to_visit or url in visited:
            pass  # this URL already in to_visit (this URL queued)
        else:
            to_visit.append(url)
        return data
    else:
        # already visited
        return id_to_data[url_to_id[url]]

''' HTML parser customized from parse_html.py-- this takes into account specfic
tags that we expect to encounter in this example'''


class MyHTMLParser(HTMLParser):
    global bs

    def handle_starttag(self, tag, attrs):
        # Only parse the 'anchor' tag.
        if tag == "a":
            # Check the list of defined attributes.
            for name, value in attrs:
                name = name.lower()
                # If href defined, print it.
                if name == "href":
                    if (value[0:9] == bs and
                       value != bs + '?Index=all'):
                        if value[0:14] == bs + "?show":
                            print "\tbranch\t" + root + value
                            add(root+value)
                        elif (value[0:len(bs + '?Index')] == bs + '?Index'):
                            print "\tbranch\t" + root + value
                            add(root+value)
                        elif value[0:17] == bs + '?esearch':
                            if len(value.strip().split("attribute=name")) > 1:
                                sv = value.split("&")
                                for s in sv:
                                    ss = s.strip()
                                    if ss[0:13] == "searchString=":
                                        if len(value.split("for=people")) > 1:
                                            ns = ss.split("=")[1]
                                            first, last = None, None
                                            try:
                                                first, last = ns.split("+")
                                            except:
                                                pass
                                                wf = open(dat_f +
                                                          "warnings.txt", "a")
                                                wf.write(root + value)
                                            print "\tperson\t" + root + value
                                            add(root + value)

'''parse by passing into a parse object'''


def parse(f):
    parser = MyHTMLParser()
    parser.feed(f)


last_datagrab = None


def grab(f):  # download and parse a given page
    print "grab", f
    global last_datagrab
    data = wget(f)
    parse(data)
    last_datagrab = data
    return data

'''
1. When visiting, URL's not-yet-visited are added to a queue to visit
2. For each URL in the queue, visit it
3. Any new URL's added during the visit, eventually need to be visited!'''


def visit(f):
    # load and parse something multi-page
    global to_visit, visited
    fn = f
    base = fn[0:30]
    if base != root + bs + "?":
        fn = root + f

    if fn in visited:
        print ("\t\talready visited")
        return

    if fn in to_visit:
        to_visit.remove(fn)

    print ("visit " + fn + " len(to_visit)= " + str(len(to_visit)) +
           " len(visited)= " + str(len(visited)))
    # "add" the URL to "the" database
    add(fn)

    base = fn[0:30]
    if base != root + bs + "?":
        print "Error"
        sys.exit(1)
    first_data = last_data = grab(fn)
    next_pg = 2
    while last_data != grab(fn + "&page="+str(next_pg)):
        if(last_data != last_datagrab):
            # register the "mult-page" URL to "the" database..
            add(fn + "&page=" + str(next_pg))
        last_data = last_datagrab
        next_pg += 1

    visited.append(fn)
    print ("endvisit " + fn + " len(to_visit)= " + str(len(to_visit)) +
           " len(visited)= " + str(len(visited)))


visit(bs + hier)  # seed the crawler

# the crawler
while len(to_visit) > 0:
    next_visit = to_visit[0]
    to_visit.remove(to_visit[0])
    visit(next_visit)

# after the crawl!
for k in url_to_id:
    print "\t", url_to_id[k], k

open(dat_f + "url_to_id", "wb").write(str(url_to_id))
open(dat_f + "id_to_url.txt", "wb").write(str(id_to_url))
# open("id_to_data-dict.txt","wb").write(str(id_to_data))

pickle.dump(url_to_id, open(dat_f + "url_to_id.p", "wb"))
pickle.dump(id_to_url, open(dat_f + "id_to_url.p", "wb"))
# pickle.dump(id_to_data, open("id_to_data.p", "wb"))  # too big

''' # Code for loading from pickle
if(False):
    url_to_id  = pickle.load(open("url_to_id.p"))
    id_to_url  = pickle.load(open("id_to_url.p"))
    id_to_data = pickle.load(open("id_to_data.p"))
'''
