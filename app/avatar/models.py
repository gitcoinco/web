# -*- coding: utf-8 -*-
"""Define the Avatar models.

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
import logging
from tempfile import NamedTemporaryFile

from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_extensions.db.fields import AutoSlugField
from easy_thumbnails.fields import ThumbnailerImageField
from economy.models import SuperModel
from github.utils import get_user
from svgutils.compose import SVG, Figure, Line

from .utils import build_avatar_component, get_svg_templates, get_upload_filename

logger = logging.getLogger(__name__)


class Avatar(SuperModel):
    """Store the options necessary to render a Gitcoin avatar."""

    class Meta:
        """Define the metadata associated with Avatar."""

        verbose_name_plural = 'Avatars'

    ICON_SIZE = (215, 215)
    config = JSONField(default=dict)
    png = models.ImageField(upload_to=get_upload_filename, null=True, blank=True)
    svg = models.FileField(upload_to=get_upload_filename, null=True, blank=True)
    use_github_avatar = models.BooleanField(default=True)

    def get_color(self, key='Background', with_hashbang=False):
        if key not in ['Background', 'ClothingColor', 'HairColor', 'ClothingColor', 'SkinTone']:
            return None
        return f"{'#' if with_hashbang else ''}{self.config.get(key)}"

    @property
    def background_color(self):
        return self.get_color() or 'FFF'

    @property
    def clothing_color(self):
        return self.get_color(key='ClothingColor') or 'CCC'

    @property
    def hair_color(self):
        return self.get_color(key='HairColor') or '4E3521'

    @property
    def skin_tone(self):
        return self.get_color(key='SkinTone') or 'EEE3C1'

    def to_dict(self):
        return self.config

    def pull_github_avatar(self):
        """Pull the latest avatar from Github and store in Avatar.png.

        Returns:
            str: The stored Github avatar URL.

        """
        from avatar.utils import get_github_avatar
        handle = self.profile_set.last().handle
        temp_avatar = get_github_avatar(handle)
        if not temp_avatar:
            return ''

        try:
            self.png.save(f'{handle}.png', ContentFile(temp_avatar.getvalue()), save=True)
            return self.png.url
        except Exception as e:
            logger.error(e)
        return ''

    @property
    def github_avatar_url(self):
        """Return the Github avatar URL."""
        if self.png and self.png.url:
            return self.png.url
        return ''

    @property
    def avatar_url(self):
        """Return the appropriate avatar URL."""
        if self.use_github_avatar and not self.png:
            return self.pull_github_avatar()
        elif self.use_github_avatar and self.png:
            return self.png.url

        if self.svg:
            return self.svg.url
        return ''

    def create_from_config(self, svg_name='avatar'):
        """Create an avatar SVG from the configuration.

        TODO:
            * Deprecate in favor of request param based view using templates.

        """
        payload = self.config
        icon_width = self.ICON_SIZE[0]
        icon_height = self.ICON_SIZE[1]

        components = [
            icon_width, icon_height,
            Line([(0, icon_height / 2), (icon_width, icon_height / 2)],
                 width=f'{icon_height}px',
                 color=f"#{payload.get('Background')}")
        ]

        for k, v in payload.items():
            if k not in ['Background', 'ClothingColor', 'HairColor', 'SkinTone']:
                components.append(
                    build_avatar_component(f"{v.get('component_type')}/{v.get('svg_asset')}", self.ICON_SIZE)
                )

        with NamedTemporaryFile(mode='w+', suffix='.svg') as tmp:
            avatar = Figure(*components)
            avatar.save(tmp.name)
            with open(tmp.name) as file:
                if self.profile_set.exists():
                    svg_name = self.profile_set.last().handle
                self.svg.save(f"{svg_name}.svg", File(file), save=True)
