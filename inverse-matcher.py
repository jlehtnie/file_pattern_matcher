#!/usr/bin/python

#   Written in 2014 by Jukka Lehtniemi
#
#   To the extent possible under law, the author(s) have
#   dedicated all copyright and related and neighboring rights
#   to this software to the public domain worldwide. This
#   software is distributed without any warranty.
#
#   You should have received a copy of the CC0 Public Domain
#   Dedication along with this software. If not, see
#   <http://creativecommons.org/publicdomain/zero/1.0/>.

import fnmatch
import re
import sys
import argparse

def get_regex(syntax, line):
    """
    >>> r1 = get_regex('glob', 'foo*bar')
    >>> bool(r1.match('foo and bar'))
    True
    >>> bool(r1.match('bar and foo'))
    False
    >>> r2 = get_regex('regexp', '^foo.*')
    >>> bool(r2.match('foobar'))
    True
    >>> bool(r2.match('barbar'))
    False
    """

    if syntax == 'glob':
        s = fnmatch.translate(line)
    else:
        s = line
    return re.compile(s)


def load_filter(filepath):
    with open(filepath) as f:
        filter = load_filter_fh(f)
    return filter


def create_test_filter_fh():
    import StringIO
    f = StringIO.StringIO()
    print >>f, '''
*.jpg jabba dabba
# comment

^.*foo\d+ foobar
'''
    f.seek(0)
    return f


def load_filter_fh(f):
    """
    >>> f = create_test_filter_fh()
    >>> filter_items = load_filter_fh(f)
    >>> len(filter_items)
    2
    >>> filter_items[0][1]
    'jabba dabba'
    """
    filter_items = []
    for line in f:
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            continue
        if line.startswith('^'):
            syntax = 'regexp'
        else:
            syntax = 'glob'
        pattern, rest = line.split(None, 1)
        regex = get_regex(syntax, pattern)
        filter_items.append((regex, rest))
    return filter_items


def main():
    parser = argparse.ArgumentParser(
            description='Match filepaths against patter list')
    parser.add_argument('--separator',
            help='Output separator default: newline', default='\n')
    parser.add_argument('--pattern-file', required=True,
            help='File with patters')
    parser.add_argument('paths', nargs='*',
            help='Paths to match against (default: read from stdin)')
    process_args(parser.parse_args())


def process_args(args):

    filter_items = load_filter(args.pattern_file)

    if args.paths:
        paths = args.paths
    else:
        paths = [x.rstrip() for x in sys.stdin.readlines()]

    result = []
    for regex, data in filter_items:
        for p in paths:
            if regex.match(p):
                result.append(data)

    if result:
        print args.separator.join(result)

if __name__ == "__main__":
    main()
