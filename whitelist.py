import fnmatch
import re

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
    with open(filepath) as f:
        filter = load_filter_fh(f)
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


if __name__ == "__main__":
    import doctest
    doctest.testmod()
