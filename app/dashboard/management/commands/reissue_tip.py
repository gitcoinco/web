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

from django.core.management.base import BaseCommand

import requests
from dashboard.models import Tip
from dashboard.utils import get_web3
from eth_account import Account
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from py_mini_racer import py_mini_racer
from secretshare import Secret, SecretShare, Share
from web3 import Web3


'''
    Queries the locally stored TIP, gets its IFPS key, 
    and re issues the txn with a higher gas value
    Saves the TxID to the tip table
'''


class Command(BaseCommand):
    help = 're issues a low gas tip'

    def add_arguments(self, parser):
        parser.add_argument('tip_id', type=int)

    def handle(self, *args, **options):

        tip_id = options['tip_id']

        if tip_id is None:
            raise Exception("tip_id must be specified")

        eth_address = "0x0000000000000000000000000000000000000000"

        tip = Tip.objects.get(pk=tip_id)

        w3 = get_web3(tip.network)

        if tip.receive_txid is None:
            raise AttributeError("Tip has had no claim attempt")
        # current_receive_tx = w3.eth.getTransactionReceipt(
        #     tip.receive_txid
        # )
        # if current_receive_tx is not None:
        #     raise ValueError(f'{tip.txid} already included in blockNumber {current_receive_tx.blockNumber}')

        tip_token_address = Web3.toChecksumAddress(
            tip.tokenAddress
        )
        tip_contract_address = Web3.toChecksumAddress(
            tip.metadata['address']
        )

        try:
            nonce = w3.eth.getTransactionCount(
                tip_contract_address
            )
            ipfs_hash = tip.metadata["reference_hash_for_receipient"]

            tip_key2 = requests.get(f'https://ipfs.infura.io:5001/api/v0/cat?arg={ipfs_hash}')
            tip_key2 = tip_key2.content
            # tip_key2 = tip_key2.encode()

            gitcoin_secret = tip.metadata["gitcoin_secret"].encode()
            # gitcoin_secret = gitcoin_secret.encode()

            print(tip_key2)
            print(gitcoin_secret)
            print("Tip Key Found")

            if tip_key2 is None:
                raise ValueError(f'Tip key not found')

            print("Combing Secrets......")
            ctx = py_mini_racer.MiniRacer()
            # load grempe secrets library
            ctx.eval("".join(open('app/assets/v2/js/lib/secrets.min.js', 'r').readlines()))
            # execute combine command
            combine_cmd = f"secrets.combine([{gitcoin_secret},{tip_key2}]);"
            computed_private_key = ctx.eval(combine_cmd)

            print(computed_private_key)

            # secret = Secret().from_bytes(b'92a077857dee02662558abf84714d26df6b441026e20bdd2f0397f955d1e54de')
            # shamir = SecretShare(2, 3, secret=secret)
            # shares = shamir.split()
            # print(shares)
            #
            # s1 = Share()
            # s2 = Share()
            # s2.from_bytes(gitcoin_secret)
            # s1.from_bytes(tip_key2)

            # shamir = SecretShare(2, 3, shares=[s1, s2])
            # computed_private_key = shamir.combine()
            # shamir = SecretShare(2, 3, shares=shares)
            # computed_private_key2 = shamir.combine()

            print(computed_private_key.to_hex())
            # print(computed_private_key2.to_hex())

            computed_account_address = Account.privateKeyToAccount(
                str(computed_private_key.to_hex())
            )
            print("Secrets Combined Successfully")
            assert computed_account_address == tip.address, "Secret Combination failed: " \
                                                            "Account address and Tip address do not match"
            gas_price = int(recommend_min_gas_price_to_confirm_in_time(2) * 10 ** 9)

            min_gas_price = int(10 ** 9)
            if gas_price < min_gas_price:
                gas_price = min_gas_price

            if tip.receive_address is None:
                raise AttributeError("Tip must be claimed by the user to use this tool")

            tip_receive_address = Web3.toChecksumAddress(
                tip.receive_address
            )

            print(tip_token_address)
            if tip_token_address is not eth_address:
                token_abi = [{
                    'inputs': [
                        {'type': 'address', 'name': 'to'},
                        {'type': 'uint256', 'name': 'amount'}
                    ],
                    'constant': False,
                    'name': 'transfer',
                    'outputs': [
                        {'type': 'bool', 'name': ''}
                    ],
                    'payable': False,
                    'type': 'function'
                }]

                contract = w3.eth.contract(
                    Web3.toChecksumAddress(
                        tip_token_address
                    ), abi=token_abi
                )

                tx = contract.functions.transfer(
                    tip_receive_address,
                    tip.amount_in_wei
                ).buildTransaction({
                    'nonce': nonce,
                    'gas': 56500,
                    'gasPrice': gas_price,
                    'value': 0
                })

            else:

                tx = {
                    'to': tip_receive_address,
                    'nonce': nonce,
                    'gas': 22000,
                    'gasPrice': gas_price,
                    'value': tip.amount_in_wei
                }

            signed = w3.eth.account.signTransaction(
                tx, computed_private_key
            )

            new_receive_txid = w3.eth.sendRawTransaction(
                signed.rawTransaction
            ).hex()
            print(f'Tip {tip_id}: Claim Resubmitted: New TxHash: {new_receive_txid}')
            tip.receive_txid = new_receive_txid
            tip.save()

        except AssertionError as e:
            print("Unable to combine secrets, check to ensure the data submitted is correct")
        except ValueError as e:
            print(e)
        except AttributeError as e:
            print(e)
