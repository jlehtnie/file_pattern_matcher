#!/usr/bin/python

import fnmatch
import re
import sys
import getopt

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
    line = line.replace(':',' ')
    _, syntax = line.split()
    if syntax in [ 'glob', 'regexp' ]:
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


def load_filter(filepath):
    f = open(filepath)
    try:
        filter = load_filter_fh(f)
    finally:
        f.close()

    return filter


def create_test_filter_fh():
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


def load_filter_fh(f):
    """
    >>> f = create_test_filter_fh()
    >>> filter = load_filter_fh(f)
    >>> len(filter)
    2
    >>> filter # doctest:+ELLIPSIS
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


def match_filter(filter, str):
    """
    >>> filter = load_filter_fh(create_test_filter_fh())
    >>> match_filter(filter, "barfoo2")
    True
    >>> match_filter(filter, "boobs.jpg")
    True
    >>> match_filter(filter, "foo 123")
    False
    >>> match_filter(filter, "smiley.gif")
    False
    """
    for regex in filter:
        if regex.search(str):
            return True
    return False


def filter_strings(filter, strings, opt_ignore=True):
    """
    >>> filter = load_filter_fh(create_test_filter_fh())
    >>> filter_strings(filter, ['foofoo1', 'head.jpg', 'foo', 'bar'], False)
    ['foofoo1', 'head.jpg']
    >>> filter_strings(filter, ['foofoo1', 'head.jpg', 'foo', 'bar'])
    ['foo', 'bar']
    """
    return [x for x in strings if match_filter(filter, x) != opt_ignore]


def usage():
    print >>sys.stderr, '''
    %s [--help] | [--pattern-file FILE] \
        [--keep-match] [--separator] [PATHS...]

    --help          Usage
    --pattern-file  Patterns to match
    --separator     Output separator (default: newline)
    --keep-match    Keep matching and ignore rest
                    (default: ignore matching and keep rest)

    PATHS   Filepaths to match against (default: read from stdin)
''' % sys.argv[0]


class Args(object): pass


def parse_args():

    try:
        opts, rest = getopt.getopt(sys.argv[1:], '',
                ['help', 'keep-match', 'separator=', 'pattern-file='])
    except getopt.GetoptError, err:
        print >>sys.stderr, str(err)
        sys.exit(2)

    args = Args()
    args.separator = '\n'
    args.opt_ignore = True
    args.pattern_file = None

    for o, a in opts:
        if o == '--help':
            usage()
            sys.exit(2)
        elif o == '--pattern-file':
            args.pattern_file = a
        elif o == '--keep-match':
            args.opt_ignore = False
        elif o == '--separator':
            args.separator = a
        else:
            assert False, 'unhandled option'

    args.paths = rest
    return args


def process_args(args):

    if (args.paths):
        paths = args.paths
    else:
        paths = [x.rstrip() for x in sys.stdin.readlines()]

    if args.pattern_file:
        filter = load_filter(args.pattern_file)
        result = filter_strings(filter, paths, args.opt_ignore)
    else:
        result = paths

    if result:
        print args.separator.join(result)


def main():

    process_args(parse_args())


if __name__ == "__main__":
    main()

