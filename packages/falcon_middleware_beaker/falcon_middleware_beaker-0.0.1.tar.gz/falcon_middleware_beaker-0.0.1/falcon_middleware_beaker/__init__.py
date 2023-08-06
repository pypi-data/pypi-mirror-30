"""falcon_middleware_beaker/__init__.py

Stores the current version for easy use accross the code-base

Copyright (C) 2018  Maciej Baranski

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

"""
import warnings

from beaker.session import SessionObject
from beaker.util import coerce_session_params

from falcon_middleware_beaker.utils import morsel_to_falcon
from falcon_middleware_beaker.version import current

__version__ = current


class BeakerSessionMiddleware(object):

    def __init__(self, config=None, environ_key='beaker.session', cookie_on_exception=True,
                 **kwargs):
        """Initialize the Session Middleware
        The Session middleware will make a lazy session instance
        available every request under the ``environ['beaker.session']``
        key by default. The location in environ can be changed by
        setting ``environ_key``.
        ``config``
            dict  All settings should be prefixed by 'session.'. This
            method of passing variables is intended for Paste and other
            setups that accumulate multiple component settings in a
            single dictionary. If config contains *no session. prefixed
            args*, then *all* of the config options will be used to
            intialize the Session objects.
        ``environ_key``
            Location where the Session instance will keyed in the WSGI
            environ
        ``**kwargs``
            All keyword arguments are assumed to be session settings and
            will override any settings found in ``config``
        """
        self.cookie_on_exception = cookie_on_exception
        config = config or {}

        # Load up the default params
        self.options = dict(invalidate_corrupt=True, type=None,
                            data_dir=None, key='beaker.session.id',
                            timeout=None, save_accessed_time=True, secret=None,
                            log_file=None)

        # Pull out any config args meant for beaker session. if there are any
        for dct in [config, kwargs]:
            for key, val in dct.items():
                if key.startswith('beaker.session.'):
                    self.options[key[15:]] = val
                if key.startswith('session.'):
                    self.options[key[8:]] = val
                if key.startswith('session_'):
                    warnings.warn('Session options should start with session. '
                                  'instead of session_.', DeprecationWarning, 2)
                    self.options[key[8:]] = val

        # Coerce and validate session params
        coerce_session_params(self.options)

        # Assume all keys are intended for session if none are prefixed with
        # 'session.'
        if not self.options and config:
            self.options = config

        self.options.update(kwargs)
        self.environ_key = environ_key

    def process_request(self, request, *args):
        session = SessionObject(request.env, **self.options)
        request.env[self.environ_key] = session

    def process_response(self, request, response, resource, request_succeded):
        session = request.env.get(self.environ_key, None)
        if (request_succeded or self.cookie_on_exception) and session.accessed():
            session.persist()
            if session.__dict__['_headers']['set_cookie']:
                cookie = session.__dict__['_headers']['cookie_out']
                if cookie:
                    cookie_parameters, cookie_keywords = morsel_to_falcon(session.cookie[session.key])
                    response.set_cookie(*cookie_parameters, **cookie_keywords)
