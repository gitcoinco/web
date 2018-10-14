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
from secrets import token_hex
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models
from django.utils.translation import gettext_lazy as _

from economy.models import SuperModel
from svgutils.compose import Figure, Line

from .exceptions import AvatarConversionError
from .utils import build_avatar_component, convert_img, get_upload_filename

logger = logging.getLogger(__name__)


class Avatar(SuperModel):
    """Store the options necessary to render a Gitcoin avatar."""

    class Meta:
        """Define the metadata associated with Avatar."""

        verbose_name_plural = 'Avatars'

    ICON_SIZE = (215, 215)

    config = JSONField(default=dict, help_text=_('The JSON configuration of the custom avatar.'), )
    # Github Avatar
    github_svg = models.FileField(
        upload_to=get_upload_filename, null=True, blank=True, help_text=_('The Github avatar SVG.')
    )
    png = models.ImageField(
        upload_to=get_upload_filename, null=True, blank=True, help_text=_('The Github avatar PNG.'),
    )
    # Custom Avatar
    custom_avatar_png = models.ImageField(
        upload_to=get_upload_filename, null=True, blank=True, help_text=_('The custom avatar PNG.'),
    )
    svg = models.FileField(
        upload_to=get_upload_filename, null=True, blank=True, help_text=_('The custom avatar SVG.'),
    )

    use_github_avatar = models.BooleanField(default=True)

    # Change tracking attributes
    __previous_svg = None
    __previous_png = None

    def __init__(self, *args, **kwargs):
        super(Avatar, self).__init__(*args, **kwargs)
        self.__previous_svg = self.svg
        self.__previous_png = self.png

    def __str__(self):
        """Define the string representation of Avatar."""
        return f"Avatar ({self.pk}) - Profile: {self.profile_set.last().handle if self.profile_set.exists() else 'N/A'}"

    def save(self, *args, force_insert=False, force_update=False, **kwargs):
        """Override the save to perform change comparison against PNG and SVG fields."""
        if (self.svg != self.__previous_svg) or (self.svg and not self.custom_avatar_png):
            # If the SVG has changed, perform PNG conversion.
            self.convert_custom_svg()
        if (self.png != self.__previous_png) or (self.png and not self.github_svg):
            # If the PNG has changed, perform SVG conversion.
            self.convert_github_png()

        super(Avatar, self).save(force_insert, force_update, *args, **kwargs)
        self.__previous_svg = self.svg
        self.__previous_png = self.png

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
        if self.use_github_avatar and not self.github_svg:
            return self.pull_github_avatar()
        if self.use_github_avatar and self.github_svg:
            return self.github_svg.url
        if self.svg:
            return self.svg.url
        return ''

    def determine_response(self, use_svg=True):
        """Determine the content type and file to serve.

        Args:
            use_svg (bool): Whether or not to use SVG format.

        """
        content_type = 'image/svg+xml' if use_svg else 'image/png'
        image = None

        if not use_svg:
            if self.use_github_avatar and self.png:
                image = self.png.file
            elif not self.use_github_avatar and self.custom_avatar_png:
                image = self.custom_avatar_png.file
        else:
            if self.use_github_avatar and self.github_svg:
                image = self.github_svg.file
            elif not self.use_github_avatar and self.svg:
                image = self.svg.file
        return image, content_type

    def get_avatar_url(self, use_svg=True):
        """Get the Avatar URL.

        Args:
            use_svg (bool): Whether or not to use SVG format.

        """
        try:
            if not use_svg:
                if self.use_github_avatar and self.png:
                    return self.png.url
                if self.use_github_avatar and not self.png:
                    return self.pull_github_avatar()
                if not self.use_github_avatar and self.custom_avatar_png:
                    return self.custom_avatar_png.url
                if not self.use_github_avatar and not self.custom_avatar_png:
                    self.convert_custom_svg(force_save=True)
                    return self.custom_avatar_png.url
            if self.use_github_avatar and self.github_svg:
                return self.github_svg.url
            if self.use_github_avatar and not self.github_svg:
                if self.png:
                    self.convert_github_png(force_save=True)
                    return self.github_svg.url
            if not self.use_github_avatar and self.svg:
                return self.svg.url
            if not self.use_github_avatar and not self.svg:
                self.create_from_config()
                return self.svg.url
        except ValueError:
            pass

        try:
            handle = self.profile_set.last().handle
        except Exception:
            handle = 'Self'

        return f'{settings.BASE_URL}dynamic/avatar/{handle}'

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

    def convert_field(self, source, target='custom_avatar_png', input_fmt='svg', output_fmt='png', force_save=False):
        """Handle converting from the source field to the target based on format."""
        try:
            # Convert the provided source to the specified output and store in BytesIO.
            tmpfile_io = convert_img(source, input_fmt=input_fmt, output_fmt=output_fmt)
            if self.profile_set.exists():
                png_name = self.profile_set.last().handle
            else:
                png_name = token_hex(8)

            if tmpfile_io:
                custom_avatar = ContentFile(tmpfile_io.getvalue())
                custom_avatar.name = f'{png_name}.{output_fmt}'
                setattr(self, target, custom_avatar)
                if force_save:
                    self.save()
                return True
        except Exception as e:
            logger.error(e)
        return False

    def convert_custom_svg(self, force_save=False):
        """Handle converting the custom Avatar SVG to PNG."""
        try:
            if not self.svg:
                self.create_from_config()

            converted = self.convert_field(
                self.svg, 'custom_avatar_png', input_fmt='svg', output_fmt='png', force_save=force_save
            )
            if not converted:
                raise AvatarConversionError('Avatar conversion error while converting SVG!')
        except AvatarConversionError as e:
            logger.error(e)

    def convert_github_png(self, force_save=False):
        """Handle converting the Github Avatar PNG to SVG."""
        try:
            if not self.png:
                self.pull_github_avatar()

            converted = self.convert_field(
                self.png, 'github_svg', input_fmt='png', output_fmt='svg', force_save=force_save
            )
            if not converted:
                raise AvatarConversionError('Avatar conversion error while converting SVG!')
        except AvatarConversionError as e:
            logger.error(e)
