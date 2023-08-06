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

import babeljs
from babeljs import conf as settings
from django import template
from django.apps import apps
from django.template import loader
from django.utils.encoding import iri_to_uri
from django.utils.safestring import mark_safe

if apps.is_installed('django.contrib.staticfiles'):
    from django.contrib.staticfiles.templatetags.staticfiles import static as _static
else:
    from django.templatetags.static import static as _static


register = template.Library()
MINIFIED = ".min" if settings.MINIFIED else ""


@register.simple_tag(takes_context=True, name="babeljs")
def tag_babeljs(context, version=settings.VERSION, minified=MINIFIED):
    return mark_safe("""<script type="text/javascript" src="{babel}"></script>""".format(
        babel=_static(iri_to_uri(
            "babeljs/{script}-{version}{minified}.js".format(
                script="browser",
                version=version,
                minified=minified,
            )
        )),
    ))


@register.simple_tag(takes_context=True, name="babel")
def babel(context, template_name):
    from babeljs import execjs

    template = loader.render_to_string(
        template_name=template_name,
        request=context['request'],
    )

    try:
        tag, js = "<script>", babeljs.transpile(template)
    except (babeljs.TransformError, execjs.RuntimeError):
        tag, js = """<script type="text/babel">""", template

    return mark_safe("".join([tag, js, "</script>"]))
