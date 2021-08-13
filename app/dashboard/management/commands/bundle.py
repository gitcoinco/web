import os
import re
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template import Context, Template
from django.template.loaders.app_directories import get_app_template_dirs

from app.bundle_context import context, templateTags
from dashboard.templatetags.bundle import render


def rmdir(loc, depth=1):
    # drop both the bundled and the bundles before recreating
    if os.path.exists(loc) and os.path.isdir(loc):
        # list all dirs/paths in the loc
        files = os.listdir(loc)

        print('%s Deleting %s assets from: %s' % ('-' * depth, len(files), loc))

        # delete files/dirs from the given loc leaving the loc dir intact
        for path in files:
            nextLoc = os.path.join(loc, path)
            if os.path.isdir(nextLoc):
                rmdir(nextLoc, depth+1)
            else:
                os.remove(nextLoc)

def rmdirs(loc, kind):
    # base path of the assets
    base = ('%s/%s/v2/' % (settings.BASE_DIR, loc)).replace('/', os.sep)
    # delete both sets of assets
    rmdir('%sbundles/%s' % (base, kind))
    rmdir('%sbundled/%s' % (base, kind))


class Command(BaseCommand):

    help = 'generates .js/.scss files from bundle template tags'

    def handle(self, *args, **options):
        """ This command will collect templates, render them with the bundleContext and run them through the bundle procedure"""

        print('\nCollect template files from all apps:')

        # get a list of all templates (rather than views to avoid segfault error that django-compressor was giving us on production)
        template_dir_list = []
        for template_dir in get_app_template_dirs('templates'):
            if settings.BASE_DIR in template_dir:
                template_dir_list.append(template_dir)

        template_list = []
        for template_dir in (template_dir_list + settings.TEMPLATES[0]['DIRS']):
            for base_dir, dirnames, filenames in os.walk(template_dir):
                for filename in filenames:
                    if ".html" in filename:
                        template_list.append(os.path.join(base_dir, filename))

        print('\n- %s templates discovered' % len(template_list))

        # using regex to grab the bundle tags content from html
        block_pattern = re.compile(r'({%\sbundle(.|\n)*?(?<={%\sendbundle\s%}))')
        open_pattern = re.compile(r'({%\s+bundle\s+(js|css|merge_js|merge_css)\s+?(file)?\s+?([^\s]*)?\s+?%})')
        close_pattern = re.compile(r'({%\sendbundle\s%})')

        print('\nClear bundle directories:\n')

        # remove the previously bundled files
        for ext in ['js', 'scss', 'css']:
            rmdirs('assets', ext)
            rmdirs('static', ext)

        print('\nStart generating bundled assets (using app.bundleContext as context):\n')

        # store unique entries for count
        rendered = dict()

        # get the tags and context from bundleContext
        tags = templateTags()
        bundleContext = context()
        # load the bundleContext into a Context instance so that it can be fed to Template.render
        bundleContext = Context(bundleContext)

        # check every template for bundle tags
        for template in template_list:
            try:
                # read the template file
                t = open(('%s' % template).replace('/', os.sep), 'r', encoding='utf8').read()
                # check for bundle tags
                if re.search(block_pattern, t):
                    for m in re.finditer(block_pattern, t):
                        block = m.group(0)
                        details = re.search(open_pattern, block)

                        # kind and name from the tag
                        kind = details.group(2)
                        name = details.group(4)

                        # remove open/close from the block
                        block = re.sub(open_pattern, '', block)
                        block = re.sub(close_pattern, '', block)

                        # add static helper to the block
                        block = '{% ' + 'load %s' % ' '.join(tags) + ' %}\n' + block

                        # create a template from the block
                        block = Template(block)

                        # render the template with bundleContext
                        block = block.render(bundleContext)

                        # render the template (producing a bundle file)
                        rendered[render(block, kind, 'file', name, True)] = True
            except Exception as e:
                print('-- X - failed to parse %s: %s' % (template, e))
                pass

        print('\n\n------------------- Generated %s bundled assets ------------------- \n\n' % len(rendered))
