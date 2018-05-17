from django.contrib import sitemaps
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from dashboard.models import Bounty, Profile
from external_bounties.models import ExternalBounty


class StaticViewSitemap(sitemaps.Sitemap):

    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return [
            'dashboard',
            'new_funding',
            'fulfill_bounty',
            'process_funding',
            'funding_details',
            'tip',
            'terms',
            'privacy',
            'cookie',
            'prirp',
            'apitos',
            'about',
            'index',
            'help',
            'whitepaper',
            'whitepaper_access',
            '_leaderboard',
            'ios',
            'faucet',
            'mission',
            'slack',
            'universe_index',
        ]

    def location(self, item):
        return reverse(item)


class IssueSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Bounty.objects.current()

    def lastmod(self, obj):
        return obj.modified_on

    def location(self, item):
        return item.get_relative_url()


class ProfileSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Profile.objects.filter(hide_profile=False).all()

    def lastmod(self, obj):
        return obj.modified_on

    def location(self, item):
        return item.get_relative_url()


class ExternalBountySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ExternalBounty.objects.filter(active=True)

    def lastmod(self, obj):
        return obj.modified_on

    def location(self, item):
        return item.url


sitemaps = {
    'static': StaticViewSitemap,
    'issues': IssueSitemap,
    'universe': ExternalBountySitemap,
    'orgs': ProfileSitemap,
}
