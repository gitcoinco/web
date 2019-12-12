# -*- coding: utf-8 -*-
"""Handle app url related tests.

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
from secrets import token_hex

from django.urls import resolve, reverse

from test_plus.test import TestCase


class AppUrlsTestCase(TestCase):
    """Define tests for app urls."""

    def setUp(self):
        self.user = self.make_user()

    def test_robotstxt_reverse(self):
        """Test the robotstxt url and check the reverse."""
        self.assertEqual(reverse('robotstxt'), '/robots.txt')

    def test_robotstxt_resolve(self):
        """Test the robotstxt url and check the resolution."""
        self.assertEqual(resolve('/robots.txt').view_name, 'robotstxt')
        self.assertEqual(resolve('/robots.txt/').view_name, 'robotstxt')

    def test_sitemap_reverse(self):
        """Test the sitemap url and check the reverse."""
        self.assertEqual(reverse('django.contrib.sitemaps.views.sitemap'), '/sitemap.xml')

    def test_sitemap_resolve(self):
        """Test the sitemap url and check the resolution."""
        self.assertEqual(resolve('/sitemap.xml').view_name, 'django.contrib.sitemaps.views.sitemap')

    def test_email_settings_reverse(self):
        """Test the email_settings url and check the reverse."""
        priv_key = token_hex(16)[:29]
        self.assertEqual(reverse('email_settings', args=(priv_key, )), f'/settings/email/{priv_key}')

    def test_email_settings_resolve(self):
        """Test the email_settings url and check the resolution."""
        self.assertEqual(resolve('/settings/email/').view_name, 'email_settings')

    def test_leaderboard_reverse(self):
        """Test the leaderboard url and check the reverse."""
        self.assertEqual(reverse('leaderboard', args=('quarterly_earners', )), '/leaderboard/quarterly_earners')

    def test_leaderboard_resolve(self):
        """Test the leaderboard url and check the resolution."""
        self.assertEqual(resolve('/leaderboard/').view_name, 'leaderboard')

    def test__leaderboard_reverse(self):
        """Test the _leaderboard url and check the reverse."""
        self.assertEqual(reverse('_leaderboard'), '/leaderboard')

    def test__leaderboard_resolve(self):
        """Test the _leaderboard url and check the resolution."""
        self.assertEqual(resolve('/leaderboard').view_name, '_leaderboard')

    def test_stats_reverse(self):
        """Test the stats url and check the reverse."""
        self.assertEqual(reverse('stats'), '/_administration/stats/')

    def test_stats_resolve(self):
        """Test the stats url and check the resolution."""
        self.assertEqual(resolve('/_administration/stats/').view_name, 'stats')

    def test_faucet_reverse(self):
        """Test the faucet url and check the reverse."""
        self.assertEqual(reverse('faucet'), '/faucet')

    def test_faucet_resolve(self):
        """Test the faucet url and check the resolution."""
        self.assertEqual(resolve('/faucet').view_name, 'faucet')
        self.assertEqual(resolve('/faucet/').view_name, 'faucet')

    def test_explorer_reverse(self):
        """Test the explorer url and check the reverse."""
        self.assertEqual(reverse('explorer'), '/explorer')

    def test_explorer_resolve(self):
        """Test the explorer url and check the resolution."""
        self.assertEqual(resolve('/explorer').view_name, 'explorer')
        self.assertEqual(resolve('/explorer/').view_name, 'explorer')

    def test_new_bounty_reverse(self):
        """Test the new_bounty url and check the reverse."""
        self.assertEqual(reverse('new_bounty'), '/bounty/new')

    def test_new_bounty_resolve(self):
        """Test the new_bounty url and check the resolution."""
        self.assertEqual(resolve('/bounty/new').view_name, 'new_bounty')
        self.assertEqual(resolve('/bounty/new/').view_name, 'new_bounty')

    def test_new_funding_reverse(self):
        """Test the new_funding url and check the reverse."""
        self.assertEqual(reverse('new_funding'), '/funding/new')

    def test_new_funding_resolve(self):
        """Test the new_funding url and check the resolution."""
        self.assertEqual(resolve('/funding/new').view_name, 'new_funding')
        self.assertEqual(resolve('/funding/new/').view_name, 'new_funding')

    def test_new_reverse(self):
        """Test the new url and check the reverse."""
        self.assertEqual(reverse('new_funding_short'), '/new')

    def test_new_resolve(self):
        """Test the new url and check the resolution."""
        self.assertEqual(resolve('/new').view_name, 'new_funding_short')
        self.assertEqual(resolve('/new/').view_name, 'new_funding_short')

    def test_uniterested_reverse(self):
        """Test the uninterested url and check the reverse"""
        self.assertEqual(reverse('uninterested', args=[1, 2]), '/actions/bounty/1/interest/2/uninterested/')

    def test_uniterested_resolve(self):
        """Test the uninterested url and check the resolution"""
        self.assertEqual(resolve('/actions/bounty/1/interest/2/uninterested/').view_name, 'uninterested')

    def test_vote_up_reverse(self):
        """Test the vote up url and check the reverse"""
        self.assertEqual(reverse('vote_tool_up', args=[1]), '/actions/tool/1/voteUp')

    def test_vote_up_resolve(self):
        """Test the vote up url and check the resolution"""
        self.assertEqual(resolve('/actions/tool/1/voteUp').view_name, 'vote_tool_up')

    def test_vote_down_reverse(self):
        """Test the vote down url and check the reverse"""
        self.assertEqual(reverse('vote_tool_down', args=[1]), '/actions/tool/1/voteDown')

    def test_vote_down_resolve(self):
        """Test the vote down url and check the resolution"""
        self.assertEqual(resolve('/actions/tool/1/voteDown').view_name, 'vote_tool_down')
