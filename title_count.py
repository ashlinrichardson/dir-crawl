#!/usr/bin/env python
'''20171117 from linear list produced from dat/* files by extract.py,
count job titles'''
import os
import sys

d = {}
lines = open("results.csv").readlines()
for i in range(0, len(lines)):
    words = lines[i].strip().split(",")
    if len(words) != 6:
        print "Error: len(words) != 6", i
        print words
        sys.exit(1)
    t = words[1].strip()
    if t == "":
        continue
    if t in d:
        d[t] += 1
    else:
        d[t] = 1

for key, value in sorted(d. iteritems(), key=lambda (k, v): (v, k)):
    print "%s: %s" % (key, value)
