# -*- coding: utf-8 -*-
"""
Copyright (C) 2018 Gitcoin Core

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

"""
from __future__ import unicode_literals

import os

from django.contrib.postgres.fields import JSONField
from django.core.files.temp import NamedTemporaryFile
from django.db import models
from django.urls import reverse

import requests
from app.storage import asset_storage, get_avatar_path
from django_extensions.db.fields import AutoSlugField
from economy.models import SuperModel
from PIL import Image, ImageOps


class Organization(SuperModel):
    """Define the structure of an Organization."""

    avatar = models.ImageField(storage=asset_storage, upload_to=get_avatar_path)
    description = models.TextField(blank=True)
    followers = models.ManyToManyField('dashboard.Profile', related_name='follows_org')
    gh_repos_data = JSONField(default={})
    gh_user_data = JSONField(default={})
    members = models.ManyToManyField('dashboard.Profile', related_name='organizations')
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name', blank=True)

    def __str__(self):
        """Return the string representation of an Organization."""
        return self.name

    def get_absolute_url(self):
        return reverse('account_organization_detail', args=(self.slug, ))

    def get_update_url(self):
        return reverse('account_organization_update', args=(self.slug, ))

    def save_avatar_from_url(self, response=None, avatar_url=''):
        """."""
        avatar_url = avatar_url or self.data.get('avatar_url', '')

        if response is None and avatar_url:
            response = requests.get(avatar_url)

        if response and response.status_code == 200:
            img_temp = NamedTemporaryFile()
            img_temp.write(response.content)
            img_temp.flush()
            img_temp.seek(0)

            image = Image.open(img_temp)
            img = Image.new('RGBA', (215, 215), (255, 255, 255))

            # execute
            image = Image.open(image, 'r').convert('RGBA')
            image = ImageOps.fit(image, (215, 215), Image.ANTIALIAS)
            offset = 0, 0
            img.paste(image, offset, image)

            # Save the thumbnail
            image.save(img_temp, 'PNG')
            img_temp.seek(0)

            try:
                self.avatar.save(f'{os.path.basename(avatar_url)}', img_temp, save=True)
            except Exception as e:
                print(f'({e}) - Failed to fetch avatar from: ({avatar_url})')
                return False
            return True
        else:
            return False
