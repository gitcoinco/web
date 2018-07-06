# -*- coding: utf-8 -*-
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
import math
import os.path
from io import BytesIO

from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
from django.db import models

import requests
from easy_thumbnails.fields import ThumbnailerImageField
from economy.models import SuperModel
from PIL import Image, ImageDraw, ImageFont


class ShortCode(SuperModel):
    """Define the EthOS Shortcode schema."""

    class Meta:
        """Define metadata associated with ShortCode."""

        verbose_name_plural = 'Short Codes'

    num_scans = models.PositiveSmallIntegerField(default=0)
    shortcode = models.CharField(max_length=255, default='')
    gif = models.FileField(null=True, upload_to='ethos/shortcodes/gifs/')
    png = models.ImageField(null=True, upload_to='ethos/shortcodes/pngs/')

    def __str__(self):
        """Define the string representation of a short code."""
        return f'ShortCode: {self.shortcode} - Scanned: ({self.num_scans})'

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

    def increment(self):
        """returns the x, y increment for this shortcode"""
        num_shortcodes = ShortCode.objects.count()
        this_position = ShortCode.objects.filter(pk__lt=self.pk).count()
        increment = math.radians((this_position / num_shortcodes) * 360)
        increment = [math.sin(increment), math.cos(increment)]
        return increment


class Hop(SuperModel):
    """Define the EthOS Hop schema."""

    class Meta:
        """Define metadata associated with Hop."""

        verbose_name_plural = 'Hops'

    # Local variables
    # Hop Graph Presets
    white = (255, 255, 255, 0)
    black = (0, 0, 0, 0)
    grey = (122, 122, 122, 0)
    size = (1000, 1000)
    center = (int(size[0]/2), int(size[1]/2))
    font = 'assets/v2/fonts/futura/FuturaStd-Medium.otf'

    # Model variables
    ip = models.GenericIPAddressField(protocol='IPv4', blank=True, null=True)
    twitter_profile = models.ForeignKey(
        'ethos.TwitterProfile', on_delete=models.SET_NULL, null=True, related_name='hops')
    txid = models.CharField(max_length=255, default='', blank=True)
    web3_address = models.CharField(max_length=255, blank=True)
    previous_hop = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True)
    shortcode = models.ForeignKey(ShortCode, related_name='hops', on_delete=models.CASCADE, null=True)
    gif = models.FileField(null=True, upload_to='ethos/shortcodes/gifs/')
    jpeg = models.ImageField(null=True, upload_to='ethos/hops/jpegs/')

    def __str__(self):
        """Define the string representation of a hop."""
        return f"{self.pk} / {self.previous_hop}"

    def increment(self):
        """Return the X, Y increment for this hop."""
        increment = self.shortcode.increment()
        return [increment[0] * self.hop_number(), increment[1] * self.hop_number()]

    def next_hop(self):
        """Return the next hop"""
        try:
            return Hop.objects.get(previous_hop=self)
        except Hop.DoesNotExist:
            return None

    def hop_number(self):
        """Get the hop number."""
        return Hop.objects.filter(shortcode=self.shortcode, pk__lt=self.pk).count() + 1

    def add_edge(self, img, loc, width=3):
        draw = ImageDraw.Draw(img)
        draw.line(loc, fill=self.grey, width=width)
        return img

    def add_node_helper(self, img, name, loc, node_image=None, size=30, font='',
                        font_size=12):
        font = font or self.font
        x, y = loc
        font = ImageFont.truetype(font, font_size, encoding="unic")
        draw = ImageDraw.Draw(img)
        x0 = x - int((size/2))
        x1 = x + int((size/2))
        y0 = y - int((size/2))
        y1 = y + int((size/2))
        loc = [x0, y0, x1, y1]

        if not node_image:
            draw.ellipse(loc, fill='blue', outline='black')
        else:
            # TODO: Debug why the circular image stored on node_image
            # renders as a square on this graph.
            pil_image_obj = Image.open(node_image).copy()
            img_x, img_y = pil_image_obj.size
            img.paste(pil_image_obj, box=(round(x), round(y)))

        d = ImageDraw.Draw(img)
        d.text((x, y), name, font=font, fill=self.black)
        return img

    def edge_size(self):
        hn = self.hop_number()
        if hn == 1:
            return 100
        return 100 + (self.hop_number() * 3)

        edge_size = 0
        previous_hop = getattr(self, 'previous_hop', None)
        if previous_hop:
            edge_size += previous_hop.edge_size()

        time_lapsed = round((self.created_on - previous_hop.created_on).total_seconds()/60) if previous_hop else 100
        this_edge_size = 0
        if 0 < time_lapsed < 30:
            this_edge_size = time_lapsed * 10
        if 0 < this_edge_size < 30:
            this_edge_size = 30
        if this_edge_size > 100:
            this_edge_size = 100

        edge_size += this_edge_size
        return edge_size


    def draw_hop(self, img):
        node_image = None
        increment = self.increment()
        # TODO -- make this based upon edge time distance
        edge_size = self.edge_size()

        coordinate_x = self.center[0] + (increment[0] * edge_size)
        coordinate_y = self.center[0] + (increment[1] * edge_size)
        node_loc = [coordinate_x, coordinate_y]
        print(f"adding node {self.pk}/{increment} at {node_loc}")
        node_image_file = self.twitter_profile.get_node_image()
        if node_image_file and getattr(node_image_file, 'file'):
            node_image = node_image_file.file

        img = self.add_node_helper(img, self.twitter_profile.username, node_loc, node_image=node_image)

        # prev_coordinate_x = center[0] + ((increment[0] - 1) * edge_size)
        # prev_coordinate_y = center[0] + ((increment[1] - 1) * edge_size)
        # prev_node_loc = [prev_coordinate_x, prev_coordinate_y]
        edge_loc = (coordinate_x, coordinate_y, self.center[0], self.center[0])
        img = self.add_edge(img, edge_loc)

        return img

    def build_graph(self, save=True, root_node='Genesis', size=None,
                    background_color=None, latest=True):
        """Build the Hop graph."""

        file_system_cache_file = f"assets/tmp/{self.pk}.gif"
        if os.path.isfile(file_system_cache_file):
            return Image.open(file_system_cache_file)

        size = size or self.size
        background_color = background_color or self.white

        img = Image.new("RGBA", self.size, color=background_color)

        if not latest and self.id and getattr(self, 'jpeg'):
            return Image.open(self.jpeg.file)
        elif not latest and self and self.id:
            hops = Hop.objects.filter(id__lte=self.id)
        else:
            hops = Hop.objects.all()

        for hop in hops:
            img = hop.draw_hop(img)

        # genesis
        img = self.add_node_helper(img, root_node, self.center)
        if not latest:
            # TODO: Save graph if not latest, so we can hop through each graph for gif building?
            pass

        img.save(file_system_cache_file)

        return img

    def build_gif(self):
        import imageio
        img_temp = NamedTemporaryFile(delete=True)
        with imageio.get_writer(img_temp.name, mode='I') as writer:
            filenames = [jpeg_file.file for jpeg_file in Hop.objects.filter(id__lte=self.id)]
            for filename in filenames:
                image = imageio.imread(filename)
                writer.append_data(image)
        img_temp.flush()
        self.gif.save(f'assets/tmp/_{self.id}.gif', File(img_temp), save=True)


class TwitterProfile(SuperModel):
    """Define the Twitter Profile."""

    profile_picture = ThumbnailerImageField(
        upload_to='ethos/twitter_profiles/',
        blank=True,
        null=True,
        max_length=255)
    node_image = models.ImageField(
        upload_to='ethos/node_images/', blank=True, null=True, max_length=255)
    username = models.CharField(max_length=255)

    class Meta:
        """Define the metadata associated with TwitterProfile."""

        verbose_name_plural = 'Twitter Profiles'

    def __str__(self):
        """Define the string representation of a twitter profile."""
        return f"Username: {self.username} - PK: ({self.pk})"

    def get_node_image(self, override=False):
        # TODO: DRY this.
        if not self.node_image or override:
            if self.profile_picture:
                image_response = requests.get(self.profile_picture['graph_node_circular'].url)
                img = Image.open(BytesIO(image_response.content))
                tmpfile_io = BytesIO()
                img.save(tmpfile_io, format=img.format)
                node_image = ContentFile(tmpfile_io.getvalue())
                node_image.name = f'{self.username}.jpg'
                self.node_image = node_image
                self.save()
        return self.node_image

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
