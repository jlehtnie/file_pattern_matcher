#!/usr/bin/python

#   Written in 2013 by Jukka Lehtniemi
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

DEFAULT_FILTER_SYNTAX = 'glob'


def parse_syntax(line):
    """
    >>> parse_syntax('syntax: glob')
    'glob'
    >>> parse_syntax('syntax: regexp')
    'regexp'
    >>> parse_syntax('syntax: none')
    Traceback (most recent call last):
    ...
    Exception: Unknown syntax "none"
    """
    line = line.replace(':', ' ')
    _, syntax = line.split()
    if syntax in ['glob', 'regexp']:
        return syntax
    else:
        raise Exception('Unknown syntax "%s"' % syntax)


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


def load_patterns(filepath):
    with open(filepath) as f:
        patterns = load_patterns_fh(f)
    return patterns


def create_test_patterns_fh():
    import StringIO
    f = StringIO.StringIO()
    print >>f, '''
*.jpg
# comment

syntax: regexp
.*foo\d+
'''
    f.seek(0)
    return f


def load_patterns_fh(f):
    """
    >>> f = create_test_patterns_fh()
    >>> patterns = load_patterns_fh(f)
    >>> len(patterns)
    2
    >>> patterns # doctest:+ELLIPSIS
    [<_sre.SRE_Pattern object at 0x...]
    """
    regexs = []
    syntax = DEFAULT_FILTER_SYNTAX
    for line in f:
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            continue
        if line.startswith('syntax'):
            syntax = parse_syntax(line)
            continue
        regexs.append(get_regex(syntax, line))
    return regexs


def match_patterns(patterns, str):
    """
    >>> patterns = load_patterns_fh(create_test_patterns_fh())
    >>> match_patterns(patterns, "barfoo2")
    True
    >>> match_patterns(patterns, "boobs.jpg")
    True
    >>> match_patterns(patterns, "foo 123")
    False
    >>> match_patterns(patterns, "smiley.gif")
    False
    """
    for regex in patterns:
        if regex.search(str):
            return True
    return False


def filter_by_patterns(patterns, paths):
    """
    >>> patterns = load_patterns_fh(create_test_patterns_fh())
    >>> filter_by_patterns(patterns, ['foofoo1', 'head.jpg', 'foo', 'bar'])
    ['foofoo1', 'head.jpg']
    """
    return [x for x in paths if match_patterns(patterns, x)]


def filter_by_shebang(shebang, paths):
    result = []
    for p in paths:
        with open(p) as f:
            s = f.readline()
            if s[0:3] == '#!/' and re.search(shebang, s):
                result.append(p)
    return result


def main():
    parser = argparse.ArgumentParser(
        description='Match filepaths against rules'
        )
    parser.add_argument(
        '--ignore-match',
        action='store_true', default=False,
        help='Ignore matching. (default: keep matching)'
        )
    parser.add_argument(
        '--separator',
        help='Output separator default: newline', default='\n'
        )
    parser.add_argument(
        '--pattern-file', required=True,
        help='File with ignore patters'
        )
    parser.add_argument(
        '--shebang',
        help='Match also if given shebang (regex) is found in file',
        default=None
        )
    parser.add_argument(
        'paths', nargs='*',
        help='Paths to match against (default: read from stdin)'
        )
    process_args(parser.parse_args())


def process_args(args):

    if args.paths:
        paths = args.paths
    else:
        paths = [x.rstrip() for x in sys.stdin.readlines()]

    patterns = load_patterns(args.pattern_file)
    result = filter_by_patterns(patterns, paths)

    if args.shebang:
        result += filter_by_shebang(args.shebang, paths)

    if args.ignore_match:
        result = [p for p in paths if p not in result]

    if result:
        print args.separator.join(result)

if __name__ == "__main__":
    main()
