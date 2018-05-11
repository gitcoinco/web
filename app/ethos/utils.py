# -*- coding: utf-8 -*-
"""Define the EthOS utilities.

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

import requests
from PIL import Image, ImageDraw, ImageOps


def get_image_file(image=None, image_url='', output_filename=''):
    """Get the Twitter user's profile picture.

        Args:
            overrider (bool): Whether or not to override the existing picture.

        """
    if not image or image_url:
        content_file = None
        try:
            if image_url:
                image = requests.get(image_url).content
            img = Image.open(BytesIO(image))
            tmpfile_io = BytesIO()
            img.save(tmpfile_io, format=img.format)
            content_file = ContentFile(tmpfile_io.getvalue())
            content_file.name = output_filename
        except Exception:
            pass
    return content_file


def get_circular_image(image):
    bigsize = (image.size[0] * 3, image.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(image.size, Image.ANTIALIAS)
    image = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    image.putalpha(mask)
    return image


def resize_image(image, width, height):
    image_width, image_height = image.size

    if width is None and height is not None:
        image_width = (image_width * height) / image_height
        image_height = height
    elif width is not None and height is None:
        image_height = (image_height * width) / image_width
        image_width = width
    elif width is not None and height is not None:
        image_width = width
        image_height = width

    return image.resize((int(image_width), int(image_height)), Image.ANTIALIAS)
