#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright (C) 2017 Siergiej Riaguzow <xor256@gmx.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar.  See the COPYING file for more details.

import mechanize
import re
import urllib2
import sys
import os
import shutil
from urlparse import urlparse

MAX_DOWNLOAD_ATTEMPTS = 5

failed_album_urls = []
song_found = False

def print_error(msg):
    color_red_bold_esc_seq = "\033[1;31m"
    color_clear_esc_seq = "\033[0;39m"
    print >> sys.stderr, '{}{}{}'.format(
        color_red_bold_esc_seq,
        msg,
        color_clear_esc_seq)

def to_MB(a_bytes):
    return a_bytes / 1024. / 1024.

def to_utf8(s):
    """ musicmp3spb.org site uses CP1251 encoding however different versions
        of python-mechanize for Python 2.7 behave differently: older versions
        return str objects in CP1251 charset and newer ones detect encoding
        automatically and return unicode objects - convert them all to UTS-8
        to enable string comparisons with UTF-8 literals in this source file
    """
    if isinstance(s, unicode):
        return s.encode('utf8')
    elif isinstance(s, str):
        return s.decode('cp1251').encode('utf8')

def download_file(url, filename):
    u = urllib2.urlopen(url)
    f = open(filename, 'wb')
    size = int(u.info().getheaders('Content-Length')[0])

    dlded = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        dlded += len(buffer)
        f.write(buffer)

        status = r'%-40s        %05.2f of %05.2f MB [%3d%%]' % \
            (to_utf8(filename), to_MB(dlded), to_MB(size), dlded * 100. / size)
        sys.stdout.write(status)
        sys.stdout.flush()
        backspaces = chr(8)*(len(status))
        sys.stdout.write(backspaces)

    sys.stdout.write('\n')
    f.close()

def browser_open(url):
    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    browser.set_handle_equiv(False)
    browser.open(url)
    return browser

def prepend_http(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        return 'http://' + url
    return url

def to_absolute_url(url, browser):
    if not url.startswith('http://') and not url.startswith('https://'):
        hostname = urlparse(browser.geturl()).hostname
        return prepend_http(hostname + url)
    return url

def mkdir_and_chdir(new_dir):
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    os.chdir(new_dir)

def download_song(url, filename_ref):
    browser = browser_open(url)

    action_regex = re.compile('/file/.*')

    filename = url + '.mp3'
    for link in browser.links(url_regex=action_regex):
        filename = to_utf8(link.text)
        break

    filename_ref['val'] = filename

    formcount=0
    for form in browser.forms():
        if action_regex.match(form.attrs['action']):
            break
        formcount=formcount+1

    browser.select_form(nr=formcount)
    browser.submit()

    for link in browser.links(url_regex='tempfile\.ru'):
        global song_found
        song_found = True
        download_file(to_absolute_url(to_utf8(link.url), browser), filename)
        break

def download_album(url):
    browser = browser_open(url)

    title_regex = re.compile('.*Скачать mp3.*', re.IGNORECASE)

    for link in browser.links(url_regex='/download/.*'):
        for attr in link.attrs:
            if len(attr) == 2 and to_utf8(attr[0]) == 'title':
                # title looks like: Скачать mp3 Arms Of The Sea,
                # links with other titles can be something like /download/play...
                # and this is not what we want to download
                if title_regex.match(to_utf8(attr[1])):
                    attempts = MAX_DOWNLOAD_ATTEMPTS
                    while attempts > 0:
                        filename_ref = { 'val': str() }
                        try:
                            song_url = to_absolute_url(to_utf8(link.url), browser)
                            download_song(song_url, filename_ref)
                            break
                        except UnicodeDecodeError:
                            filename = filename_ref['val']
                            if filename and os.path.exists(filename):
                                os.remove(filename)
                            raise e
                        except Exception as e:
                            attempts -= 1
                            print_error('\nFailure, attempts left: %d, song: %s\n\t%s!' % \
                                (attempts, song_url, e))
                            filename = filename_ref['val']
                            if filename and os.path.exists(filename):
                                os.remove(filename)
                            # Rethrow exception to the upper level so it can cleanup
                            # album directory i case we cannot download one song 5 times
                            if attempts == 0:
                                raise e

def download_band(url):
    browser = browser_open(url)

    first_link = True
    for link in browser.links(url_regex='/album/.*'):
        album_url = to_absolute_url(to_utf8(link.url), browser)
        album_name = to_utf8(link.text)
        if not album_name: # Invisible, there will be another one with text
            continue
        album_dir = './' + album_name

        print '-------------------------------------------------------------------------------'
        print '  Album "%s"' % album_name
        print '  %s' % album_url
        print '-------------------------------------------------------------------------------'

        attempts = MAX_DOWNLOAD_ATTEMPTS
        while attempts > 0:
            mkdir_and_chdir(album_dir)
            try:
                download_album(album_url)
                os.chdir('..')
                break
            except Exception as e:
                attempts -= 1
                print_error('\nFailure, attempts left: %d, album: %s\n\t%s!' % \
                    (attempts, album_url, e))
                os.chdir('..')
                shutil.rmtree(album_dir, ignore_errors=True)
                if attempts == 0:
                    global failed_album_urls
                    failed_album_urls.append(album_url)
def main():
    if len(sys.argv) < 2 or \
       len(sys.argv) > 2 and \
       sys.argv[1] != '-a' and sys.argv[1] != '--all':
        script_name = os.path.basename(sys.argv[0])
        print_error('Usage: %s <album_url> or %s -a[--all] <band_url>' % (script_name, script_name))
        print_error('To print help: %s -h[--help]' % script_name)
        sys.exit(1)

    arg = sys.argv[1]
    was_error = False

    if arg == '-h' or arg == '--help':
        help()
    elif arg == '-a' or arg == '--all':
        url = prepend_http(sys.argv[2])
        try:
            download_band(url)
        except Exception as e:
            was_error = True
            print_error('Error: Cannot download band albums: %s\n\t%s!' % (url, e))
    else:
        url = prepend_http(sys.argv[1])
        try:
            download_album(url)
        except Exception as e:
            was_error = True
            print_error('Error: Cannot download album: %s\n\t%s!' % (url, e))

        if not was_error and not song_found:
            print_error("Found nothing to download!")
        elif failed_album_urls:
            print_error('\nFailed to download the following albums:')
            for album_url in failed_album_urls:
                print_error('\t' + album_url)

def help():
    print """Python script to automatically download albums from http://musicmp3spb.org site.

Usage:

$ musicmp3spb.py http://musicmp3spb.org/album/dualism.html
to download all songs from the album's page

or
$ musicmp3spb.py -a[--all] http://musicmp3spb.org/artist/textures.html
to download all albums from the band's page.

You need Python2 (since mechanize is not available for Pyton3)
and mechanize (https://pypi.python.org/pypi/mechanize)."""

if __name__ == '__main__':
    main()
