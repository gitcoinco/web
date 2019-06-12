# -*- coding: utf-8 -*-
"""Define the Grant subminer management command.

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

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'inserts contributions into the DB'

    def handle(self, *args, **options):
        # setup
        handle = 'gitcoinbot'
        token_addr = '0x89d24a6b4ccb1b6faa2625fe562bdd9a23260359'
        contributor_address = '0x620a3981f796346df02be83fd929758a88078e3c'
        token_symbol = 'DAI'
        network = 'mainnet'

        from dashboard.models import Profile
        from grants.models import Grant, Contribution, Subscription
        from grants.views import record_subscription_activity_helper
        items = [[82,13548,'0x37059e9ef5463d73b74641ae2bb1664b42e90b908aceff2871715390794d60e8'],[89,11728,'0xa4ce2dffcaef66bf0d8ba884a71f12a65752137b06ab4f6722c76cef493b223a'],[24,3499,'0x79c0160f59766c42095fd06f3d43453fe6d8cd253892e93ad3fd378d04427a44'],[39,3450,'0x37059e9ef5463d73b74641ae2bb1664b42e90b908aceff2871715390794d60e8'],[80,2762,'0x532d4f821ebab104a3923af0507cdbe09dabd2ff7f70b5a557fdd3abc2a4dbdf'],[48,2346,'0xb9abbb52df9decbae56f24b236987c4a31444ed00297a87471ef5192c233628f'],[25,2085,'0x532d4f821ebab104a3923af0507cdbe09dabd2ff7f70b5a557fdd3abc2a4dbdf'],[20,1428,'0x37059e9ef5463d73b74641ae2bb1664b42e90b908aceff2871715390794d60e8'],[13,1245,'0x79c0160f59766c42095fd06f3d43453fe6d8cd253892e93ad3fd378d04427a44'],[36,910,'0x79c0160f59766c42095fd06f3d43453fe6d8cd253892e93ad3fd378d04427a44'],[37,868,'0x532d4f821ebab104a3923af0507cdbe09dabd2ff7f70b5a557fdd3abc2a4dbdf'],[40,774,'0x3e03360481585dfc7ae3bdd5bb18a439126ba84f390a5bff96e8f6a6292d5e13'],[49,725,'0x37059e9ef5463d73b74641ae2bb1664b42e90b908aceff2871715390794d60e8'],[85,725,'0x37059e9ef5463d73b74641ae2bb1664b42e90b908aceff2871715390794d60e8'],[21,720,''],[12,530,'0x9ec5d4b9db048ebdec6951b9b856531e13f73fe215acd7aafa8bd59d75070b44'],[32,527,'0x79c0160f59766c42095fd06f3d43453fe6d8cd253892e93ad3fd378d04427a44'],[30,354,'0x37059e9ef5463d73b74641ae2bb1664b42e90b908aceff2871715390794d60e8'],[29,301,'0x37059e9ef5463d73b74641ae2bb1664b42e90b908aceff2871715390794d60e8'],[16,265,'0x37059e9ef5463d73b74641ae2bb1664b42e90b908aceff2871715390794d60e8'],[86,261,'0x5e3e271ba1329a267ebb8e717650a0420179477abd6f0badfaddfdfe151899ac'],[38,158,'0x37059e9ef5463d73b74641ae2bb1664b42e90b908aceff2871715390794d60e8'],[65,157,'0xa4ce2dffcaef66bf0d8ba884a71f12a65752137b06ab4f6722c76cef493b223a'],[17,150,'0x532d4f821ebab104a3923af0507cdbe09dabd2ff7f70b5a557fdd3abc2a4dbdf'],[47,119,'0x4a66b9da1b98d1b0f9d749fd7379b56cc0b4c3ca45823dff52e54bd203553b3a'],[81,100,'0xa4ce2dffcaef66bf0d8ba884a71f12a65752137b06ab4f6722c76cef493b223a'],[99,59,'0x37059e9ef5463d73b74641ae2bb1664b42e90b908aceff2871715390794d60e8'],[23,56,'0x074c6edbd446cf45fd0431e8c6cc7aa8e40a1f8c0c180367259e80b305a24be1'],[35,28,'0x532d4f821ebab104a3923af0507cdbe09dabd2ff7f70b5a557fdd3abc2a4dbdf'],[62,24,'0x532d4f821ebab104a3923af0507cdbe09dabd2ff7f70b5a557fdd3abc2a4dbdf'],[41,16,'0x37059e9ef5463d73b74641ae2bb1664b42e90b908aceff2871715390794d60e8'],[50,15,'0xa4ce2dffcaef66bf0d8ba884a71f12a65752137b06ab4f6722c76cef493b223a'],[43,13,'0x3e03360481585dfc7ae3bdd5bb18a439126ba84f390a5bff96e8f6a6292d5e13'],[31,10,'0xfc1ca568c041944ecfa5864d9b3cf911fcec73cea0288330e48dc89b2c9a4458'],[74,0,'0x37059e9ef5463d73b74641ae2bb1664b42e90b908aceff2871715390794d60e8'],[76,0,'0x37059e9ef5463d73b74641ae2bb1664b42e90b908aceff2871715390794d60e8'],[26,0,'0x298585812a7890dde47304249044955487c0c1d11b38c579bbd2228fdcd5c62d'],[87,0,'0x37059e9ef5463d73b74641ae2bb1664b42e90b908aceff2871715390794d60e8'],[15,0,'0x6f971c2320439d5d618eb1682cc46afabc96021bc01a00929a89adfc01dd6d21'],[73,0,'0x532d4f821ebab104a3923af0507cdbe09dabd2ff7f70b5a557fdd3abc2a4dbdf'],[63,0,'0x37059e9ef5463d73b74641ae2bb1664b42e90b908aceff2871715390794d60e8'],[79,0,'0x532d4f821ebab104a3923af0507cdbe09dabd2ff7f70b5a557fdd3abc2a4dbdf'],[66,0,'0x532d4f821ebab104a3923af0507cdbe09dabd2ff7f70b5a557fdd3abc2a4dbdf'],[72,0,'0x532d4f821ebab104a3923af0507cdbe09dabd2ff7f70b5a557fdd3abc2a4dbdf'],[92,0,'0x532d4f821ebab104a3923af0507cdbe09dabd2ff7f70b5a557fdd3abc2a4dbdf'],[83,0,'']]

        for item in items:
            grant_id = item[0]
            amount = item[1]
            tx_id = item[2]
            print(grant_id)
            grant = Grant.objects.get(pk=grant_id)
            profile = Profile.objects.get(handle=handle)
            subscription = Subscription()

            subscription.active = False
            subscription.contributor_address = contributor_address
            subscription.amount_per_period = amount
            subscription.real_period_seconds = 0
            subscription.frequency = 1
            subscription.frequency_unit = 'days'
            subscription.token_address = token_addr
            subscription.token_symbol = token_symbol
            subscription.gas_price = 1
            subscription.new_approve_tx_id = '0x0'
            subscription.num_tx_approved = 1
            subscription.network = network
            subscription.contributor_profile = profile
            subscription.grant = grant
            subscription.save()

            subscription.successful_contribution(tx_id);
            subscription.error = True #cancel subs so it doesnt try to bill again
            subscription.subminer_comments = "skipping subminer bc this is a 1 and done subscription, and tokens were alredy sent"
            subscription.save()
            record_subscription_activity_helper('new_grant_contribution', subscription, profile)
