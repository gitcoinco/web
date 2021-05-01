import hashlib
import os
import re

from django import template
from django.conf import settings
from django.templatetags.static import static

from bs4 import BeautifulSoup

register = template.Library()


"""
    Creates bundles from linked and inline javascript or CSS into a single file - ready to be compressed by webpack.

    Syntax:

        {% compress2 <js/css> file [block_name] %}
        <script src=""></script>
        <script>
            ...
        </script>
        --or--
        <link href=""/>
        <style>
            ...
        </style>
        {% endcompress2 %}

    (dev) to compress:

        yarn run webpack

    (prod) to compress:

        ./manage.py compress2 && yarn run build
"""

def css_elems(soup):
    return soup.find_all({'link': True, 'style': True})


def js_elems(soup):
    return soup.find_all('script')


def get_tag(kind, src):
    return '<script src="%s"></script>' % src if kind == "js" else '<link rel="stylesheet" href="%s"/>' % src


def render(block, kind, mode, name='asset', forced=False):

    if settings.ENV not in ['prod'] or forced == True:
        content = ''
        attr = 'src' if kind == 'js' else 'href'
        soup = BeautifulSoup(block, "lxml")

        # construct the content by converting tags to import statements
        for el in js_elems(soup) if kind == 'js' else css_elems(soup):
            if el.get(attr):
                # removes static url and erroneous quotes from path
                cleanUri = el[attr].replace(settings.STATIC_URL, '').replace('"', '').replace("'", '')
                # import the scripts from the assets dir
                if kind == 'js':
                    content += 'import \'%s/assets/%s\';\n' % (settings.BASE_DIR, cleanUri)
                else:
                    content += ' @import \'%s/assets/%s\';\n' % (settings.BASE_DIR, cleanUri)

            else:
                # content held within tags after cleaning up all whitespace on each newline (consistent content regardless of indentation)
                content += '\n'.join(str(x).strip() for x in (''.join([str(x) for x in el.contents]).splitlines()))

        # create a hash from the block content
        chash = hashlib.md5(content.encode('utf')).hexdigest()
        # absolute path on disk to the bundle we are generating
        fname = ('%s/assets/v2/%s/bundles/%s.%s.%s' % (settings.BASE_DIR, kind, name, chash[0:6], kind)).replace('/', os.sep)
        # ensure the bundles directory exists
        os.makedirs(os.path.dirname(fname), exist_ok=True)
        # open the file in read/write mode
        f = open(fname, 'a+', encoding='utf8')
        f.seek(0)
        # if content (of the block) has changed - write new content
        if f.read() != content:
            # clear the file before writing new content
            f.truncate(0)
            f.write(content)
            f.close()
            # print so that we have concise output in the compress2 command
            print('- Generated: %s' % fname)

    # in production and not forced we will just return the static bundle
    return get_tag(kind, static('v2/%s/bundled/%s.%s.%s' % (kind, name, chash[0:6], 'css' if kind == 'scss' else kind)))


class CompressorNode(template.Node):


    def __init__(self, nodelist, kind=None, mode='file', name=None):
        self.nodelist = nodelist
        self.kind = kind
        self.mode = mode
        self.name = name


    def render(self, context, forced=False):
        return render(self.nodelist.render(context), self.kind, self.mode, self.name)


@register.tag
def compress2(parser, token):
    # pull content and split args from compress2 block
    nodelist = parser.parse(('endcompress2',))
    parser.delete_first_token()

    args = token.split_contents()

    if not len(args) in (2, 3, 4):
        raise template.TemplateSyntaxError(
            "%r tag requires either one or three arguments." % args[0])

    kind = 'scss' if args[1] == 'css' else args[1]

    if len(args) >= 3:
        mode = args[2]
    else:
        mode = 'file'
    if len(args) == 4:
        name = args[3]
    else:
        name = None

    return CompressorNode(nodelist, kind, mode, name)
