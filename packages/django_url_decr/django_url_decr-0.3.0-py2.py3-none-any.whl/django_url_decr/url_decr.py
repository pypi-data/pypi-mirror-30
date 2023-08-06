import functools
import copy
import django
from django.conf.urls import url
if django.VERSION >= (2, 0):
    from django.urls import URLPattern, URLResolver


    class RegexURLPattern:
          pass


    class RegexURLResolver:
          pass
else:
    try:
        from django.urls import RegexURLPattern, RegexURLResolver
    except ImportError:
        from django.core.urlresolvers import RegexURLPattern, RegexURLResolver


    class URLPattern:
        pass


    class URLResolver:
        pass


def copy_url_component(source):
    '''
    Recursively copy RegexURLPattern and RegexURLResolver objects.
    Since copy.deepcopy is unusable.
    '''
    curr = copy.copy(source)
    if isinstance(curr, RegexURLPattern):
        return curr
    if isinstance(curr, URLPattern):
        return curr
    elif isinstance(curr, (URLResolver, RegexURLResolver)):
        curr.url_patterns = list(map(copy_url_component, curr.url_patterns))
        return curr
    else:
        raise Exception("Unknown url pattern type %s."\
                        % repr(type(curr)))


def dummy_decr(func):
    '''
    A dummy decorator
    '''
    @functools.wraps(func)
    def wrap(*sub, **kw):
        print("Calling %s" % func.__name__)
        ret = func(*sub, **kw)
        return ret
    return wrap


def iter_pattern(pattern):
    '''
    Iterate through patterns.
    '''
    stack = [(0, pattern)]
    while stack:
        level, curr = stack.pop()
        if isinstance(curr, (RegexURLPattern, URLPattern)):
            yield level, curr
        elif isinstance(curr, (RegexURLResolver, URLResolver)):
            for p in curr.url_patterns:
                stack.append((level + 1, p))
        else:
            raise Exception("Unknown url pattern type %s."\
                            % repr(type(curr)))


def url_decr(*sub, **kw):
    decr = kw.pop('decr', None)
    pattern = url(*sub, **kw)
    if decr:
        pattern = copy_url_component(pattern)
        for __, p in iter_pattern(pattern):
            # For django<1.10.1
            if hasattr(p, '_callback') and callable(p._callback):
                p._callback = decr(p._callback)
            elif callable(p.callback):
                p.callback = decr(p.callback)
    return pattern
