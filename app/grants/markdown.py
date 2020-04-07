from typing import Optional
import re
import markdown
from markdown.inlinepatterns import LinkInlineProcessor, LINK_RE
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.urls import reverse, resolve, Resolver404, NoReverseMatch


class Error(Exception):
    pass


class InvalidMarkdown(Error):

    def __init__(self, error: str, value: Optional[str] = None) -> None:
        self.error = error
        self.value = value

    def __str__(self) -> str:
        if self.value is None:
            return self.error
        return f'{self.error} "{self.value}"';


def get_site_domain() -> str:
    return 'gitcoin.co'


def clean_link(href: str, site_domain: str) -> str:
    if href.startswith('mailto:'):
        email_match = re.match('^(mailto:)?([^?]*)', href)
        if not email_match:
            raise InvalidMarkdown('Invalid mailto link', value=href)

        email = email_match.group(2)
        if email:
            try:
                EmailValidator()(email)
            except ValidationError:
                raise InvalidMarkdown('Invalid email address', value=email)

        return href

    # Remove fragments or query params before trying to match the url name
    href_parts = re.search(r'#|\?', href)
    if href_parts:
        start_ix = href_parts.start()
        url_name, url_extra = href[:start_ix], href[start_ix:]
    else:
        url_name, url_extra = href, ''

    try:
        url = reverse(url_name)
    except NoReverseMatch:
        pass
    else:
        return url + url_extra

    parsed_url = urlparse(href)

    if parsed_url.netloc == site_domain:
        try:
            resolver_match = resolve(parsed_url.path)
        except Resolver404:
            raise InvalidMarkdown(
                "Should not use absolute links to the current site.\n"
                "We couldn't find a match to this URL. Are you sure it exists?",
                value=href,
            )
        else:
            raise InvalidMarkdown(
                'Should not use absolute links to the current site.\n'
                'Try using the url name "{}".'.format(resolver_match.url_name),
                value=href,
            )

    if parsed_url.scheme not in ('http', 'https'):
        raise InvalidMarkdown('Must provide an absolute URL (be sure to include https:// or http://)', href)

    return href


class DjangoLinkInlineProcessor(LinkInlineProcessor):
    def getLink(self, data, index):
        href, title, index, handled = super().getLink(data, index)
        site_domain = get_site_domain()
        href = clean_link(href, site_domain)
        return href, title, index, handled


class DjangoUrlExtension(markdown.Extension):
    def extendMarkdown(self, md, *args, **kwrags):
        md.inlinePatterns.register(DjangoLinkInlineProcessor(LINK_RE, md), 'link', 160)
