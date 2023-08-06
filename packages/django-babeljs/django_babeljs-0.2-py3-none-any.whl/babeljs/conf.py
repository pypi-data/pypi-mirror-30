# Copyright (C) 2007-2018, Raffaele Salmaso <raffaele@salmaso.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from os.path import abspath, dirname, join

from django.conf import settings as djsettings

VERSION = "5.8.33"
BABELJS = getattr(djsettings, "BABELJS_BABEL", "browser-{}.min.js".format(VERSION))
JS_ROOT = getattr(djsettings, "BABELJS_ROOT", abspath(join(dirname(__file__), "static/babeljs")))
DEBUG = getattr(djsettings, "DEBUG")
MINIFIED = getattr(djsettings, "BABELJS_MINIFIED", not DEBUG)
CACHE_BACKEND = getattr(djsettings, "BABELJS_CACHE_BACKEND", "default")
CACHE_TIMEOUT = getattr(djsettings, "BABELJS_CACHE_TIMEOUT", 300)
