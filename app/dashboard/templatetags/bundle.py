import hashlib
import os
import re

from django import template
from bs4 import BeautifulSoup
from django.conf import settings
from django.templatetags.static import static

register = template.Library()

"""
    Creates bundles from linked and inline Javascript or SCSS into a single file - compressed by py or webpack.

    Syntax:

        {% bundle [js|css|merge_js|merge_css] file [block_name] %}
        <script src="..."></script>
        <script>
            ...
        </script>
        --or--
        <link href="..."/>
        <style>
            ...
        </style>
        {% endbundle %}

    (dev) to compress:

        yarn run webpack

    (prod) to compress:

        ./manage.py bundle && yarn run build
"""

def css_elems(soup):
    return soup.find_all({'link': True, 'style': True})


def js_elems(soup):
    return soup.find_all('script')


def get_tag(ext, src):
    return '<script src="%s"></script>' % src if ext == "js" else '<link rel="stylesheet" href="%s"/>' % src


def check_merge_changes(elems, attr, outputFile):
    # fn checks if content is changed since last op
    changed = False
    # if the block exists as a file - get timestamp so that we can perform cheap comp
    blockTs = 0
    try:
        blockTs = os.path.getmtime(outputFile)
    except:
        pass
    # if any file has changed then we need to regenerate
    for el in elems:
        # removes static url and erroneous quotes from path
        asset = '%s/assets/%s' % (settings.BASE_DIR, el[attr])
        # bundle straight to the bundled directory skipping 'bundles'
        ts = -1
        try:
            ts = os.path.getmtime(asset.replace('/', os.sep))
        except:
            pass
        # if any ts is changed then we regenerate
        if ts < blockTs:
            changed = True
            break

    return changed


def get_content(elems, attr, kind, merge):
    # concat all input in the block
    content = ''
    # construct the content by converting tags to import statements
    for el in elems:
        # is inclusion or inline tag?
        if el.get(attr):
            # removes static url and erroneous quotes from path
            asset = '%s/assets/%s' % (settings.BASE_DIR, el[attr])
            # if we're merging the content then run through minify and skip saving of intermediary
            if merge:
                # bundle straight to the bundled directory skipping 'bundles'
                f = open(asset.replace('/', os.sep), 'r', encoding='utf8')
                f.seek(0)
                c = f.read()
                # for production we should minifiy the assets
                if settings.ENV in ['prod'] and kind == 'merge_js':
                    import jsmin
                    c = jsmin.jsmin(c, quote_chars="'\"`")
                elif settings.ENV in ['prod'] and kind == 'merge_css':
                    import cssmin
                    c = cssmin.cssmin(c)
                # place the content with a new line sep
                content += c + '\n'
            else:
                # import the scripts from the assets dir
                if kind == 'js':
                    content += 'import \'%s\';\n' % asset
                else:
                    content += ' @import \'%s\';\n' % asset
        else:
            # content held within tags after cleaning up all whitespace on each newline (consistent content regardless of indentation)
            content += '\n'.join(str(x).strip() for x in (''.join([str(x) for x in el.contents]).splitlines()))

    return content


def render(block, kind, mode, name='asset', forced=False):
    # check if we're merging content
    merge = True if 'merge' in kind else False
    ext = kind.replace('merge_', '')

    # output locations
    bundled = 'bundled'
    bundles = 'bundles' if not merge else bundled

    # clean up the block -- essentially we want to drop anything that gets added by staticfinder (could we improve this by not using static in the templates?)
    cleanBlock = block.replace(settings.STATIC_URL, '')
    # drop any quotes that are NOT immediately inside brackets
    cleanBlock = re.sub(re.compile(r'(?<!\()(\'|\")(?!\))'), '', cleanBlock)
    # in production staticfinder will attach an additional hash to the resource which doesnt exist on the local disk
    if settings.ENV in ['prod'] and forced != True:
        cleanBlock = re.sub(re.compile(r'(\..{12}\.(css|scss|js))'), r'.\2', cleanBlock)

    # parse block with bs4
    soup = BeautifulSoup(cleanBlock, "lxml")
    # get a hash of the block we're working on (after parsing -- ensures we're always working against the same input)
    blockHash = hashlib.sha256(str(soup).encode('utf')).hexdigest()

    # In production we don't need to generate new content unless we're running this via the bundle command
    if settings.ENV not in ['prod'] or forced == True:
        # concat all input in the block
        content = ''
        # pull the appropriate tags from the block
        elems = js_elems(soup) if ext == 'js' else css_elems(soup)
        attr = 'src' if ext == 'js' else 'href'
        # output disk location (hard-coding assets/v2 -- this could be a setting?)
        outputFile = ('%s/assets/v2/%s/%s/%s.%s.%s' % (settings.BASE_DIR, bundles, ext, name, blockHash[0:6], ext)).replace('/', os.sep)
        changed = True if merge == False or forced == True else check_merge_changes(elems, attr, outputFile)

        # !merge kind is always tested - merge is only recreated if at least one of the inclusions has been altered
        if changed:
            # retrieve the content for the block/output file
            content = get_content(elems, attr, kind, merge)
            # ensure the bundles directory exists
            os.makedirs(os.path.dirname(outputFile), exist_ok=True)
            # open the file in read/write mode
            f = open(outputFile, 'a+', encoding='utf8')
            f.seek(0)

            # if content (of the block) has changed - write new content
            if merge or f.read() != content:
                # clear the file before writing new content
                f.truncate(0)
                f.write(content)
                f.close()
                # print so that we have concise output in the bundle command
                print('- Generated: %s' % outputFile)

    # in production and not forced we will just return the static bundle
    return get_tag(ext, static('v2/%s/%s/%s.%s.%s' % (bundled, ext, name, blockHash[0:6], 'css' if ext == 'scss' else ext)))


class CompressorNode(template.Node):


    def __init__(self, nodelist, kind=None, mode='file', name=None):
        self.nodelist = nodelist
        self.kind = kind
        self.mode = mode
        self.name = name


    def render(self, context, forced=False):
        return render(self.nodelist.render(context), self.kind, self.mode, self.name)


@register.tag
def bundle(parser, token):
    # pull content and split args from bundle block
    nodelist = parser.parse(('endbundle',))
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
