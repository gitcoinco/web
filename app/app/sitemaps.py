from django.contrib import sitemaps
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from dashboard.models import Bounty, Profile
from kudos.models import Token


class StaticViewSitemap(sitemaps.Sitemap):

    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return [
            'dashboard', 'new_funding', 'tip', 'terms', 'privacy', 'cookie', 'prirp', 'apitos', 'about', 'index',
            'help', 'whitepaper', 'whitepaper_access', '_leaderboard', 'faucet', 'mission', 'slack', 'labs', 'results',
            'activity', 'kudos_main', 'kudos_marketplace', 'grants', 'funder_bounties'
        ]

    def location(self, item):
        if item == 'grants':
            return reverse('grants:grants')
        return reverse(item)


class IssueSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Bounty.objects.current().cache()

    def lastmod(self, obj):
        return obj.modified_on

    def location(self, item):
        return item.get_relative_url()


class KudosSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Token.objects.filter(hidden=False)

    def lastmod(self, obj):
        return obj.modified_on

    def location(self, item):
        return item.get_relative_url()


class ProfileSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Profile.objects.filter(hide_profile=False).cache()

    def lastmod(self, obj):
        return obj.modified_on

    def location(self, item):
        return item.get_relative_url()


class ContributorLandingPageSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        from retail.utils import programming_languages
        return programming_languages + ['']

    def lastmod(self, obj):
        from django.utils import timezone
        return timezone.now()

    def location(self, item):
        return f'/bounties/contributor/{item}'


class ResultsSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        from retail.utils import programming_languages
        return programming_languages

    def lastmod(self, obj):
        from django.utils import timezone
        return timezone.now()

    def location(self, item):
        import urllib.parse
        item = urllib.parse.quote_plus(item)
        return f'/results/{item}'


sitemaps = {
    'landers': ContributorLandingPageSitemap,
    'results': ResultsSitemap,
    'static': StaticViewSitemap,
    'issues': IssueSitemap,
    'orgs': ProfileSitemap,
    'kudos': KudosSitemap,
}
