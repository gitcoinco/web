'''
    Copyright (C) 2020 Gitcoin Core

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

from django.core.management.base import BaseCommand

from dashboard.models import Profile


# We use this command rather than profiles.json fixture,
# because otherwise it could overwrite existing data in the DB.
class Command(BaseCommand):

    help = 'creates gitcointbot profile'

    def handle(self, *args, **options):
        Profile.objects.create(handle='gitcoinbot',
                               suppress_leaderboard=True,
                               hide_profile=False,
                               hide_wallet_address=False,
                               trust_profile=True,
                               dont_autofollow_earnings=True,
                               show_job_status=False,
                               data={"id": None,
                                     "bio": None,
                                     "url": "",
                                     "blog": "",
                                     "name": "Gitcoin.co Bot",
                                     "type": "User",
                                     "email": "gitcoinbot@gitcoin.co",
                                     "login": "gitcoinbot",
                                     "company": "GitCoin",
                                     "node_id": "",
                                     "hireable": None,
                                     "html_url": "https://github.com/gitcoinbot",
                                     "location": "",
                                     "followers": 0,
                                     "following": 0,
                                     "gists_url": "https://api.github.com/users/gitcoinbot/gists{/gist_id}",
                                     "repos_url": "https://api.github.com/users/gitcoinbot/repos",
                                     "avatar_url": "https://avatars2.githubusercontent.com/u/27903976?s=460&u=55f8ae7c0f451691d93ea0ad5b89b58d1282981b&v=4",
                                     "created_at": "2016-02-20T13:42:34Z",
                                     "events_url": "https://api.github.com/users/gitcoinbot/events{/privacy}",
                                     "site_admin": true,
                                     "updated_at": "2016-02-27T08:15:49Z",
                                     "gravatar_id": "",
                                     "starred_url": "https://api.github.com/users/gitcoinbot/starred{/owner}{/repo}",
                                     "public_gists": 0,
                                     "public_repos": 0,
                                     "followers_url": "https://api.github.com/users/gitcoinbot/followers",
                                     "following_url": "https://api.github.com/users/gitcoinbot/following{/other_user}",
                                     "organizations_url": "https://api.github.com/users/gitcoinbot/orgs",
                                     "subscriptions_url": "https://api.github.com/users/gitcoinbot/subscriptions",
                                     "received_events_url": "https://api.github.com/users/gitcoinbot/received_events"})
