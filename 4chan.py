#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Alexis Nootens <me@axn.io>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

import sys, os, re, json, argparse, urllib.request as req

class Post:
    def __init__(self, no, tim=None, ext=None, filename=None):
        self.no  = no
        self.tim = tim
        self.ext = ext
        self.filename = filename

    def hasimage(self):
        return self.filename is not None

def getdocument(url):
    try:
        return req.urlopen(url)
    except req.URLError as e:
        print(e.reason)
        req.urlcleanup()
    sys.exit(1)

def download(argv, board, post):
    url = "http://i.4cdn.org/{}/{}{}".format(board, post.tim, post.ext)
    filename = "{}{}".format(post.filename if argv.f else post.tim, post.ext)

    if argv.directory is not None:
        if not os.path.exists(argv.directory):
            os.makedirs(argv.directory)
        filename = "{}/{}".format(argv.directory, filename)

    print("Downloading:", filename)
    req.urlretrieve(url, filename)

def parse(argv, board, thread):
    url = "http://a.4cdn.org/{}/thread/{}.json".format(board, thread)
    res = getdocument(url).read()
    posts = []

    json.loads(res.decode(), object_hook=lambda post:
               posts.append(Post(post.get('no'),  post.get('tim'),
                                 post.get('ext'), post.get('filename'))))

    try:
        for post in posts:
            if post.hasimage():
                download(argv, board, post)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        req.urlcleanup()

def main(argv):
    url = argv.thread
    pattern = re.compile(r'(?:http[s]?://)?boards\.4chan\.org/([a-z0-9]{1,3})/thread/(\d*)(?:#p\d*)?')

    if pattern.match(url):
        ctx = re.search(pattern, url).groups()
        parse(argv, board=ctx[0], thread=ctx[1])
    else:
        print("Not a valid URL thread")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download images from an 4chan thread')
    parser.add_argument('-f', '--filename', dest='f', action='store_true', help='preserve filenames (default: no)')
    parser.add_argument('-d', dest='directory', type=str, required=False, metavar='DIRECTORY',
                        help='set the directory to save the files (default: current)')
    parser.add_argument('thread', type=str, help='the thread url')
    main(parser.parse_args())
