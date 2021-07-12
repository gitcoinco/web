"""Define the burn kudos management command.

Copyright (C) 2021 Gitcoin Core

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
from django.core.management.base import BaseCommand

from dashboard.models import Profile
from kudos.models import Token, TokenRequest
from kudos.tasks import mint_token_request


def delete_town_square_posts():
    from django.utils import timezone
    from dashboard.models import Profile
    then = timezone.now() - timezone.timedelta(hours=12)

    gcb = Profile.objects.get(handle='gitcoinbot')
    activities = gcb.activities.filter(activity_type='created_kudos', created_on__gt=then)
    activities.delete()


class Command(BaseCommand):

    help = 'mints all kudos in the platform on xdai'

    def handle(self, *args, **options):
        # config
        counter = 0
        trs = TokenRequest.objects.filter(approved=True, network='mainnet')
        print(trs.count())
        for token in trs:
            try:
                already_xdaid = TokenRequest.objects.filter(network='xdai', name=token.name)
                if not already_xdaid:
                    token.pk = None
                    token.network = 'xdai'
                    token.save()
                    print(f'-/- {token.pk}')
                    mint_token_request(token.pk, send_notif_email=False)
                    delete_town_square_posts()
            except Exception as e:
                print(e)

        for token in Token.objects.filter(contract__network='mainnet'):
            if token.gen == 1 and not token.on_xdai:
                try:
                    tr = TokenRequest.objects.create(
                        network='xdai',
                        name=token.name,
                        description=token.description,
                        priceFinney=token.price_finney,
                        artist=token.artist if token.artist else '',
                        platform=token.platform if token.platform else '',
                        to_address=token.owner_address,
                        numClonesAllowed=token.num_clones_allowed,
                        artwork_url=token.image,
                        metadata=token.metadata,
                        tags=token.tags.split(','),
                        approved=True,
                        profile=Profile.objects.get(handle='gitcoinbot'),
                        processed=True,
                        )
                    print(f'*/* {tr.pk}')
                    mint_token_request(tr.pk, send_notif_email=False)
                    
                    # post - minting hooks; like transfering over info or deleting townsquare posts
                    delete_town_square_posts()
                    if token.on_xdai:
                        ku = token.on_xdai
                        if ku.on_mainnet:
                            if ku.on_mainnet.preview_img_mode == 'svg':
                                if ku.preview_img_mode == 'png':
                                    ku.preview_img_mode = ku.on_mainnet.preview_img_mode
                                    print(ku.id)
                                    ku.save()

                except Exception as e:
                    print(e)
