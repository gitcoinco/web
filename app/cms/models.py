# -*- coding: utf-8 -*-
'''
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

'''
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page


class GuideSection(blocks.StructBlock):
    heading = blocks.CharBlock()
    paragraph = blocks.RichTextBlock(required=False)
    html = blocks.RawHTMLBlock(required=False)


class GuideSectionWrapper(blocks.StreamBlock):
    section = GuideSection()


class GuidePage(Page):
    intro = RichTextField(blank=True)
    sections = StreamField(GuideSectionWrapper())

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        StreamFieldPanel('sections')
    ]
