import os
import re
import shutil

from django.core.management.base import BaseCommand
from django.template.loaders.app_directories import get_app_template_dirs
from django.conf import settings

from dashboard.templatetags.compress2 import render


def rmdir(loc):
    # drop both the bundled and the bundles before recreating
    if os.path.exists(loc) and os.path.isdir(loc):
        print('- Deleting assets from: %s' % loc)
        shutil.rmtree(loc)

def rmdirs(loc, kind):
    # base path of the assets
    base = ('%s/%s/v2/%s/' % (settings.BASE_DIR, loc, kind)).replace('/', os.sep)
    # delete both sets of assets
    rmdir('%sbundles' % base)
    rmdir('%sbundled' % base)


class Command(BaseCommand):

    help = 'creates .js/.scss files from compress2 template tags'

    def handle(self, *args, **options):
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

        # using regex to grab the compress2 tags content from html
        block_pattern = re.compile(r'({%\scompress2(.|\n)*?(?<={%\sendcompress2\s%}))')
        open_pattern = re.compile(r'({%\s+compress2\s+(js|css)\s+?(file)?\s+?([^\s]*)?\s+?%})')
        close_pattern = re.compile(r'({%\sendcompress2\s%})')
        static_open_pattern = re.compile(r'({%\sstatic\s["|\'])')
        static_close_pattern = re.compile(r'(\s?%}(\"|\')?\s?\/?>)')

        # remove the previously bundled files
        rmdirs('assets', 'js')
        rmdirs('assets', 'scss')
        rmdirs('static', 'js')
        rmdirs('static', 'scss')

        print('\nStart generating bundle files\n')

        count = 0
        for template in template_list:
            try:
                f = open(('%s' % template).replace('/', os.sep), 'r', encoding='utf8')

                t = f.read()
                if re.search(block_pattern, t) is not None:
                    for m in re.finditer(block_pattern, t):
                        block = m.group(0)
                        details = re.search(open_pattern, block)

                        # kind and name from the tag
                        kind = 'scss' if details.group(2) == 'css' else details.group(2)
                        name = details.group(4)

                        # remove open/close from the block
                        block = re.sub(open_pattern, '', block)
                        block = re.sub(close_pattern, '', block)

                        # clean static helper if we havent ran this through parse
                        block = re.sub(static_open_pattern, '', block)
                        block = re.sub(static_close_pattern, '>', block)

                        # render the template (producing a bundle file)
                        render(block, kind, 'file', name, True)

                        # counting the number of generated files
                        count+=1

            except Exception as e:
                # print('-- X - failed to parse %s: %s' % (template, e))
                pass

        print('\nGenerated %s bundle files%s' % (count, ' - remember to run `yarn run build` then `./manage.py collectstatic --i other --no-input`\n' if settings.ENV in ['prod'] else ''))
