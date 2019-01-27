'''
    Copyright (C) 2017 Gitcoin Core

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
from django.db import transaction
from event_ethdenver2019.models import Event_ETHDenver2019_Customizing_Kudos
from kudos.models import KudosTransfer
from dashboard.utils import get_nonce, get_web3
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from kudos.utils import kudos_abi
from web3 import Web3
from dashboard.models import Profile


class Command(BaseCommand):

    help = 'check all participants of ETHDenver2019 and distribute the final kudos upon collecting all required ones'

    def handle(self, *args, **options):
#        all_kudos_collected = True
        print(f'sanity checks and initial data load...')
        final_kudos = Event_ETHDenver2019_Customizing_Kudos.objects.filter(active=True,final=True).first()
        print(f"The final kudos is defined as... {final_kudos.kudos_required}")
        if final_kudos is None:
            print('No final kudos defined in the customizing table - please define and run again.')
            return
        kudos_selected = Event_ETHDenver2019_Customizing_Kudos.objects.filter(active=True,final=False).all()
        print(f"amount of kudos to collect: {kudos_selected.count()}")


        kudosReq = []
        for ku in kudos_selected:
            kudosReq.append(ku.kudos_required)

        kudos_select = KudosTransfer.objects.filter(kudos_token_cloned_from__in=kudosReq,receive_address__isnull=False).all()
        #print(kudos_select)

        destinct_addrs = []
        for res in kudos_select:
            if not res.receive_address in destinct_addrs and res.receive_address != '':
                destinct_addrs.append(res.receive_address)

        print(f'addresses: {destinct_addrs}')
        for addr in destinct_addrs:
            print(f"checking {addr}...")

            all_kudos_collected = True
            for kudos in kudos_selected:
                recv = kudos_select.filter(kudos_token_cloned_from=kudos.kudos_required, receive_address=addr).last()
                if recv is None:
                    all_kudos_collected = False

            # if kudos_select.filter(receive_address=addr).count() == kudos_selected.count():
            if all_kudos_collected is True:
                print(f'user qualifies for final token, checking for final token...')
                if KudosTransfer.objects.filter(kudos_token_cloned_from=final_kudos.kudos_required, receive_address=addr).count() > 0:
                    print(f'user already got final token, skipping.')
                else:
                    print(f'user should receive final token now... initiating transfer')
                    address = Web3.toChecksumAddress(addr)
                    kudos_contract_address = Web3.toChecksumAddress(settings.KUDOS_CONTRACT_MAINNET)
                    kudos_owner_address = Web3.toChecksumAddress(settings.KUDOS_OWNER_ACCOUNT)
                    w3 = get_web3(settings.KUDOS_NETWORK)
                    contract = w3.eth.contract(Web3.toChecksumAddress(kudos_contract_address), abi=kudos_abi())
                    tx = contract.functions.clone(address, final_kudos.kudos_required.token_id, 1).buildTransaction({
                        'nonce': get_nonce(settings.KUDOS_NETWORK, kudos_owner_address),
                        'gas': 500000,
                        'gasPrice': int(recommend_min_gas_price_to_confirm_in_time(5) * 10**9),
                        'value': int(1 / 1000.0 * 10**18),
                    })

                    signed = w3.eth.account.signTransaction(tx, settings.KUDOS_PRIVATE_KEY)
                    txid = w3.eth.sendRawTransaction(signed.rawTransaction).hex()

                    with transaction.atomic():
                        kudos_transfer = KudosTransfer.objects.create(
                            emails=['event@ethdenver.org'],
                            # For kudos, `token` is a kudos.models.Token instance.
                            kudos_token_cloned_from=final_kudos.kudos_required,
                            amount=0,
                            comments_public='Congratulations on completing the ETHDenver2019 Challenge!',
                            ip='127.0.0.1',
                            github_url='',
                            from_name=Profile.objects.filter(handle='owocki').handle,
                            from_email='',
                            from_username=Profile.objects.filter(handle='owocki'),
                            network=settings.KUDOS_NETWORK,
                            from_address=settings.KUDOS_OWNER_ACCOUNT,
                            receive_address=addr,
                            is_for_bounty_fulfiller=False,
                            metadata={'event': True},
                            # sender_profile='',
                            txid=txid,
                            receive_txid=txid,
                            tx_status='pending',
                            receive_tx_status='pending',
                        )

        print('finished processing event kudos.')
        '''
        for kudos in kudos_selected:
            recv = kudos_select.filter(kudos_token_cloned_from=kudos.kudos_required).last()
            if recv is None:
                all_kudos_collected = False

        if all_kudos_collected:
            page_ctx['success'] = True
        else:
            page_ctx['success'] = False
        pass
        '''
