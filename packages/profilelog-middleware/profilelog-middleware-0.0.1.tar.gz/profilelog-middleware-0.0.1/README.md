# ProfileLogMiddleware

This is a WSGI middleware which will profile the request and embed it in the response. The default behavior is to embed the profiling data via `console.table`, right before the closing `<html>` tag. The result is that you can then see the information by opening devtools (should work on both Chrome and Firefox):

![](https://github.com/chromano/profilelog-middleware/blob/master/sample.png "Chrome devtools")

## Installation

    pip install -e git+https://github.com/chromano/profilelog-middleware.git#egg=profilelog-middleware
    
## Usage

Simply wrap your WSGI application with `profilelog.middleware.ProfileLogMiddleware`. Below is an example for the `wsgi.py` file provided with Django projects:

    import os

    from django.core.wsgi import get_wsgi_application
    from profilelog.middleware import ProfileLogMiddleware

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

    application = ProfileLogMiddleware(get_wsgi_application())

## Config

You can specify to the middleware how far you want to go by specifying the number of function calls to display. Example:

    application = ProfileLogMiddleware(get_wsgi_application(), limit=5)

The default value for `limit` is 25, which should suffice for most usecases.
