"""falcon_middleware_beaker/utils.py

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
from falcon.util.misc import http_date_to_dt


def morsel_to_falcon(morsel):
    parameters = [morsel.key, morsel.coded_value]
    keywords = dict()

    for name in (
        'expires',
        'path',
        'domain',
        'max_age',
        'secure',
    ):
        value = morsel[name.replace('_', '-')] or None
        if name == 'expires':
            value = http_date_to_dt(value, obs_date=True) if value else None
        elif name == 'max_age':
            value = int(value) if value else None
        elif name in 'secure':
            value = bool(value)
        keywords[name] = value
    keywords['http_only'] = bool(morsel.get('httponly', None))
    return parameters, keywords
