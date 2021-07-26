import hashlib
import os
import re

from django import template
from django.conf import settings
from django.templatetags.static import static

from bs4 import BeautifulSoup

register = template.Library()


"""
    Creates bundles from linked and inline Javascript or SCSS into a single file - compressed by py or webpack.

    Syntax:

        {% bundle [js|css|scss|merge_js|merge_css] file [block_name] %}
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


# check for production env
isProduction = settings.ENV in ['prod']


# define variables to include in every script (and react to any changes)
sassVars = [
    '/assets/v2/scss/lib/bootstrap/_functions',
    '/assets/v2/scss/lib/bootstrap/_variables',
    '/assets/v2/scss/lib/bootstrap/_mixins',
    '/assets/v2/scss/gc-variables',
    '/assets/v2/scss/lib/bootstrap-overrides'
]


def css_elems(block):
    return block.find_all({'link': True, 'style': True})


def js_elems(block):
    return block.find_all('script')


def get_tag(ext, src):
    return '<script src="%s"></script>' % src if ext == "js" else '<link rel="stylesheet" href="%s"/>' % src


def get_file_ts(asset, reportException=False):
    ts = 0
    try:
        ts = os.path.getmtime(asset.replace('/', os.sep))
    except Exception as e:
        if reportException:
            print(e)
    return ts


def clean_block_and_hash(block):
    # clean up the block -- we want to drop anything that gets added by staticfinder (we could remove this if we purge {% static ... %} from tags)
    if isProduction:
        # in prod - staticfinder will attach static_url and an additional hash to the resource which doesn't exist on the local disk
        block = re.sub(re.compile(r'(' + re.escape(settings.STATIC_URL) + r')([^>]*)(\.[0-9a-zA-Z]{12})?\.(css|scss|js)'), r'\2.\4', block)
    else:
        # in dev - we still need to drop the static_url (but the hash will be absent)
        block = block.replace(settings.STATIC_URL, '')

    # parse block with bs4
    block = BeautifulSoup(block, "lxml")
    # get a hash of the block we're working on (after parsing the stripped down block -- ensures we're always hashing the same input)
    blockHash = hashlib.sha256(str(block).encode('utf')).hexdigest()

    # return tuple with details
    return block, blockHash


def check_for_changes(elems, attr, kind, outputFile):
    # fn checks if content has changed since last op
    changed = False
    # if the block already exists as a file - get timestamp so that we can perform cheap comp
    blockTs = get_file_ts(outputFile)

    # if vars are altered - all blocks must be updated
    if 'css' in kind:
        for varFile in sassVars:
            ts = get_file_ts(settings.BASE_DIR + varFile + '.scss')
            if ts > blockTs:
                changed = True
                # break as soon as any marks changed
                break

    # if any imported files have changed then we need to regenerate
    if not changed:
        for el in elems:
            if el.get(attr):
                # check if we're loading an alternative source in production
                file = el[attr]
                if isProduction and el.get('prod'):
                    file = el['prod']

                # discover ts using the absolute path of the given asset
                if not el.get('base-dir'):
                    ts = get_file_ts('%s/assets/%s' % (settings.BASE_DIR, file), True)
                else:
                    ts = get_file_ts(os.path.normpath(os.path.join(settings.BASE_DIR, '../', el['base-dir'].strip('/'), file.strip('/'))), True)

                # if any of the imported files is newer than the block then we need to regenerate
                if ts == 0 or ts > blockTs:
                    changed = True
                    # break as soon as any marks changed
                    break

    # if the imports are newer then save a new version (inline block changes will generate a new outputFile hash)
    return True if blockTs == 0 else changed


def get_sass_extras():
    # additional vars/functions to pass into sass.compile
    sassExtras = '''
        $mode: '%s';
        @function static($url) {
            @if (str-slice($url, 1, 1) == '/') {
                $url: str-slice($url, 2);
            }
            @return '%s' + $url;
        };
    ''' % (settings.ENV, settings.STATIC_URL)

    # attach variable files to sassExtras
    for varFile in sassVars:
        sassExtras += '@import "%s"; ' % (settings.BASE_DIR + varFile)

    return sassExtras


def get_bundled(elems, attr, kind, merge):
    # concat all input in the block
    content = ''
    # construct a bundle by converting tags to import statements or by merging the raw content
    for el in elems:
        # is inclusion or inline block?
        if el.get(attr):

            # check if we're loading an alternative source in production
            file = el[attr]
            if isProduction and el.get('prod'):
                file = el['prod']

            # absolute path of the given asset
            if not el.get('base-dir'):
                asset = '%s/assets/%s' % (settings.BASE_DIR, file)
            else:
                asset = os.path.normpath(os.path.join(settings.BASE_DIR, '../', el['base-dir'].strip('/'), file.strip('/')))

            # merged content is read from file and concatenated
            if merge:
                f = open(asset.replace('/', os.sep), 'r', encoding='utf8')
                f.seek(0)
                c = f.read()
                # separate each content block with a line sep
                content += c + '\n'
            else:
                # bundles are made up of appropriate import statements (to be imported and compiled by webpack)
                if 'js' in kind:
                    content += 'import \'%s\';\n' % asset
                else:
                    content += '@import \'%s\';\n' % asset
        else:
            # concat content held within tags after cleaning up all whitespace on each newline (consistent content regardless of indentation)
            content += '\n'.join(str(x).strip() for x in (''.join([str(x) for x in el.contents]).splitlines()))

    # compile any sass to css
    if 'css' in kind:
        import sass
        content = sass.compile(string='%s \n %s' % (get_sass_extras(), content))

    # minify the content in production
    if isProduction and 'js' in kind:
        import rjsmin
        content = rjsmin.jsmin(content)
    elif isProduction and 'css' in kind:
        import rcssmin
        content = rcssmin.cssmin(content)

    # content is compiled and minified (if in production)
    return content


def render(block, kind, mode, name='asset', forced=False):
    # check if we're merging content
    merge = True if 'merge' in kind else False
    # ext is used to position the output on disk
    ext = kind.replace('merge_', '')

    # save all scss/css/merge_css to the same dir
    ext = 'css' if 'css' in ext else ext

    # output locations
    bundled = 'bundled'
    # webpack bundles need to be placed into the watched dir
    bundles = 'bundles' if kind == 'js' else bundled

    # clean the block and get a hash of the content
    block, blockHash = clean_block_and_hash(block)

    # in production we don't need to generate new content unless we're running this via the bundle command
    if not isProduction or forced == True:
        # concat all input in the block
        content = ''
        # pull the appropriate tags from the block
        elems = js_elems(block) if ext == 'js' else css_elems(block)
        attr = 'src' if ext == 'js' else 'href'
        # output disk location (hard-coding assets/v2 -- this could be a setting?)
        outputFile = ('%s/assets/v2/%s/%s/%s.%s.%s' % (settings.BASE_DIR, bundles, ext, name, blockHash[0:6], ext)).replace('/', os.sep)
        # check if content was altered since last op
        changed = check_for_changes(elems, attr, kind, outputFile)

        # only create for new bundles or if at least one of the inclusions has been altered
        if changed:
            # retrieve the content for the block/output file
            content = get_bundled(elems, attr, kind, merge)
            # ensure the bundles directory exists
            os.makedirs(os.path.dirname(outputFile), exist_ok=True)
            # open the file in read/write mode
            f = open(outputFile, 'a+', encoding='utf8')
            f.seek(0)
            # clear the file before writing new content
            f.truncate(0)
            f.write(content)
            f.close()
            # print so that we have concise output in the bundle command
            print('- Generated: %s' % outputFile)

    # in production and not forced we will just return the static bundle
    return get_tag(ext, static('v2/%s/%s/%s.%s.%s' % (bundled, ext, name, blockHash[0:6], ext)))


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

    # retrieve the arguments
    args = token.split_contents()

    # ensures the correct number of arguments
    if not len(args) in (2, 3, 4):
        raise template.TemplateSyntaxError(
            "%r tag requires either one or three arguments." % args[0])

    # kind can be js|css|scss|merge_js|merge_css
    kind = args[1]

    # not including inline yet so mode will always be file
    mode = 'file'

    # file name for the output
    name = args[3] if len(args) == 4 else None


    return CompressorNode(nodelist, kind, mode, name)
