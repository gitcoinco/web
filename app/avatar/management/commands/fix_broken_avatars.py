'''
    Copyright (C) 2021 Gitcoin Core

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.

'''

from django.core.management.base import BaseCommand

from avatar.models import *


class Command(BaseCommand):

    help = 'fixes avatars whose pngs have failed'


    def handle(self, *args, **options):
        avatars = CustomAvatar.objects.filter(png='').order_by('-pk')
        for avatar in avatars:
            try:
                avatar.png = avatar.convert_field(avatar.svg, 'svg', 'png')
                avatar.hash = BaseAvatar.calculate_hash(Image.open(BytesIO(avatar.png.read())))
                avatar.save()
                print(avatar.png, avatar.png.url)
            except Exception as e:
                print(avatar.pk, e)
