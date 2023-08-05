"""WSGI middleware for including profile logging together with HTML response.

Provided is a wrapper class `ProfileLogMiddleware` that you can use on a WSGI
application. Just wrap your WSGI application object with it and you are set.

For example, Django projects usually have a wsgi.py file with a global
application object, so all you have to do is:

    application = ProfileLogMiddleware(application)

If you want to provide arguments to the middlware, do it after passing the
application object. For example:

    application = ProfileLogMiddleware(application, limit=5)

Please refer to AUTHORS file for credits and LICENSE for licensing info.
"""
import json

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

try:
    from cProfile import Profile
except ImportError:
    from profile import Profile

from pstats import Stats


def _bytes(content):
    try:
        return bytes(content,  'utf-8')
    except TypeError:
        return bytes(content)


def html_writer(env, original, profile):
    """Rewrite HTML responses to include profiling info.

    If a closing <body> tag can't be found, the profiling info won't be added.
    """
    term = b'</body>'
    idx = original.lower().rfind(term)
    if idx == -1:
        return

    profile_output = """<script>
console.group("Profiling log from remote {} {}");
console.table({});
console.groupEnd();
</script>
""".format(env.get('REQUEST_METHOD'), env.get('PATH_INFO'), json.dumps(profile))

    response = original[:idx]
    response += _bytes(profile_output)
    response += original[idx:]

    return response


class ProfileLogMiddleware(object):
    """Middleware for profiling requests and embeding results in the response.

    First, and most important, parameter is the WSGI application that you are
    supposed to already have. Optional parameters are:

      - `limit`: The maximum number of function calls to include. Please note
    that function calls are sorted by most expensive (in terms of time) first.
    If you want to get the full profiling data, use -1.

      - `logwriter`: A callable which takes the WSGI environ dict, the original
    response and a list of dicts containing profiling data and optionally
    returns a new response.  The inner dict has the following keys:

        - `source`: The callable name
        - `call_count`: The number of times the callable was called.
        - `total_time`: Milliseconds spent on this callable
    """
    def __init__(self, application, limit=25, logwriter=html_writer):
        self.application = application
        self.limit = limit
        self.logwriter = logwriter

    def __call__(self, environ, start_response):
        response = []

        def _start_response(status, headers, exc_info=None):
            start_response(status, headers, exc_info)
            return response.append

        def runapp():
            leftover = self.application(environ, _start_response)
            response.extend(leftover)
            if hasattr(leftover, 'close'):
                leftover.close()

        profile = Profile()
        profile.runcall(runapp)

        body = b''.join(response)
        buff = StringIO()
        stats = Stats(profile, stream=buff).sort_stats(2)

        table = []
        for func in stats.fcn_list[:self.limit]:
            cc, nc, tt, ct, callers = stats.stats[func]
            table.append({
                'source': '{}@{}:{}'.format(func[2], func[0], func[1]),
                'call_count': nc,
                'total_time': ct,
            })

        custom_response = self.logwriter(environ, body, table)
        if custom_response:
            return [custom_response]

        return [body]
