"""Define the EthOS models.

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

from io import BytesIO

from django.core.files.base import ContentFile
from django.db import models

import requests
from economy.models import SuperModel
from PIL import Image


class ShortCode(SuperModel):
    """Define the EthOS Shortcode schema."""

    class Meta:
        """Define metadata associated with ShortCode."""

        verbose_name_plural = 'ShortCodes'

    num_scans = models.PositiveSmallIntegerField(default=0)
    shortcode = models.CharField(max_length=255, default='')
    gif = models.FileField(null=True, upload_to='ethos/shortcodes/gifs/')
    png = models.ImageField(null=True, upload_to='ethos/shortcodes/pngs/')

    def get_latest_chart_png(self):
        """Get the latest chart for the Shortcode in PNG format."""
        pass

    def get_latest_chart_gif(self):
        """Get the latest chart for the Shortcode in GIF format."""
        pass

    def save(self, *args, **kwargs):
        """Override the save to handle building and storing the chart assets."""
        self.get_latest_chart_png()
        self.get_latest_chart_gif()
        super().save(*args, **kwargs)


class Hop(SuperModel):
    """Define the EthOS Hop schema."""

    class Meta:
        """Define metadata associated with Hop."""

        verbose_name_plural = 'Hops'

    ip = models.GenericIPAddressField(protocol='IPv4')
    twitter_username = models.CharField(max_length=255)
    twitter_profile_pic = models.URLField()
    twitter_profile = models.ForeignKey(
        'ethos.TwitterProfile', on_delete=models.SET_NULL, null=True, related_name='hops')
    txid = models.CharField(max_length=255, default='')
    web3_address = models.CharField(max_length=255)
    previous_hop = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True)
    shortcode = models.ForeignKey(ShortCode, related_name='hops', on_delete=models.CASCADE, null=True)
    gif = models.FileField(null=True, upload_to='ethos/shortcodes/gifs/')
    png = models.ImageField(null=True, upload_to='ethos/hops/pngs/')

    def get_current_hop_chart_png():
        """Generate the current Hop state as a PNG."""
        pass

    def get_current_hop_chart_gif():
        """Generate the current Hop state as a GIF."""
        pass


class TwitterProfile(SuperModel):
    """Define the Twitter Profile."""

    profile = models.ForeignKey('dashboard.Profile', blank=True, null=True, on_delete=models.SET_NULL)
    profile_picture = models.ImageField(
        upload_to='ethos/twitter_profiles/',
        blank=True,
        null=True,
        max_length=255)
    username = models.CharField(max_length=255)

    class Meta:
        """Define the metadata associated with TwitterProfile."""

        verbose_name_plural = 'Twitter Profiles'

    def get_picture(self, override=False):
        """Get the Twitter user's profile picture.

        Args:
            overrider (bool): Whether or not to override the existing picture.

        """
        if not self.profile_picture or override:
            image_url = f'https://twitter.com/{self.username}/profile_image?size=original'
            try:
                image_response = requests.get(image_url)
                img = Image.open(BytesIO(image_response.content))
                tmpfile_io = BytesIO()
                img.save(tmpfile_io, format=img.format)
                profile_picture = ContentFile(tmpfile_io.getvalue())
                profile_picture.name = f'{self.username}.jpg'
                self.profile_picture = profile_picture
            except Exception:
                pass

    def save(self, *args, **kwargs):
        """Override the save to handle fetching and storing the profile picture."""
        self.get_picture()
        super().save(*args, **kwargs)
