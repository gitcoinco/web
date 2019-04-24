from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import Http404
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from dashboard.utils import get_nonce, get_web3
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from kudos.models import BulkTransferCoupon, BulkTransferRedemption, KudosTransfer, Token
from kudos.utils import kudos_abi
from ratelimit.decorators import ratelimit
from retail.helpers import get_ip
from web3 import Web3

from .models import Event_ETHDenver2019_Customizing_Kudos


'''
def ethdenver2019_redeem(request):
    profile = get_profile(request)
    if profile is None:
        return TemplateResponse(request, 'ethdenver2019/notloggedin.html', {})

    kudos_select = KudosTransfer.objects.filter(recipient_profile=profile).all()

    all_kudos_collected = True
    kudos_selected = Event_ETHDenver2019_Customizing_Kudos.objects.filter(active=True).all()

    for kudos in kudos_selected:
        recv = kudos_select.filter(kudos_token_cloned_from=kudos.kudos_required).last()
        if recv is None:
            all_kudos_collected = False

    page_ctx = {
        "profile": profile
        }
    if all_kudos_collected:
        page_ctx['success'] = True
    else:
        page_ctx['success'] = False

    return TemplateResponse(request, 'ethdenver2019/redeem.html', page_ctx)
'''

def ethdenver2019(request):
    recv_addr = 'invalid'
    if request.GET:
        recv_addr = request.GET.get('eth_addr', 'invalid')
    if not recv_addr.lower().startswith("0x"):
        recv_addr = f"0x{recv_addr}"
        
    kudos_select = KudosTransfer.objects.filter(receive_address=recv_addr).all()

    i_kudos_item = 0
    kudos_selection = []
    kudos_row = []
    kudos_selected = Event_ETHDenver2019_Customizing_Kudos.objects.filter(active=True, final=False).all()
    all_kudos_collected = True

    for kudos in kudos_selected:
        kudos_obj = {
            "kudos": kudos.kudos_required,
            "received": False,
            "customizing": kudos,
            # "expanded_kudos": vars(kudos.kudos_required)
        }
        recv = kudos_select.filter(kudos_token_cloned_from=kudos.kudos_required).last()
        if recv is not None:
            kudos_obj['received'] = True
            kudos_obj['transfer'] = recv
        else:
            all_kudos_collected = False

        kudos_row.append(kudos_obj)
        i_kudos_item = i_kudos_item + 1

    if i_kudos_item > 0:
        kudos_selection.append(kudos_row)

    page_ctx = {
        "kudos_selection": kudos_selection,
        "page2": request.GET and recv_addr != 'invalid',
        "page3": all_kudos_collected
    }

    page_ctx["page1"] = not page_ctx['page2']
    if page_ctx["page1"] == True:
        #disable popover
        page_ctx["page3"] = False

    return TemplateResponse(request, 'ethdenver2019/onepager.html', page_ctx)


@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
def receive_bulk_ethdenver(request, secret):

    coupons = BulkTransferCoupon.objects.filter(secret=secret)
    if not coupons.exists():
        raise Http404

    coupon = coupons.first()

    kudos_transfer = ""
    if coupon.num_uses_remaining <= 0:
        messages.info(request, f'Sorry but this kudos redeem link has expired! Please contact the person who sent you the coupon link, or contact your nearest Gitcoin representative.')
        return redirect(coupon.token.url)

    error = False
    if request.POST:
        try:
            address = Web3.toChecksumAddress(request.POST.get('forwarding_address'))
        except:
            error = "You must enter a valid Ethereum address (so we know where to send your Kudos). Please try again."
        if not error:
            address = Web3.toChecksumAddress(request.POST.get('forwarding_address'))
            already_claimed = KudosTransfer.objects.filter(receive_address=address,kudos_token_cloned_from=coupon.token)
            if already_claimed.count() > 0:
                messages.info(request, f'You already redeemed this kudos! If you think this wrong contact the ETHDenver Team!')
                return redirect(coupon.token.url)
            ip_address = get_ip(request)

            private_key = settings.KUDOS_PRIVATE_KEY if not coupon.sender_pk else coupon.sender_pk
            kudos_owner_address = settings.KUDOS_OWNER_ACCOUNT if not coupon.sender_address else coupon.sender_address

            kudos_contract_address = Web3.toChecksumAddress(settings.KUDOS_CONTRACT_MAINNET)
            kudos_owner_address = Web3.toChecksumAddress(kudos_owner_address)
            w3 = get_web3(coupon.token.contract.network)
            nonce = w3.eth.getTransactionCount(kudos_owner_address)
            contract = w3.eth.contract(Web3.toChecksumAddress(kudos_contract_address), abi=kudos_abi())
            tx = contract.functions.clone(address, coupon.token.token_id, 1).buildTransaction({
                'nonce': nonce,
                'gas': 500000,
                'gasPrice': int(recommend_min_gas_price_to_confirm_in_time(1) * 10**9),
                'value': int(coupon.token.price_finney / 1000.0 * 10**18),
            })

            try:
                signed = w3.eth.account.signTransaction(tx, private_key)
                txid = w3.eth.sendRawTransaction(signed.rawTransaction).hex()

                with transaction.atomic():
                    kudos_transfer = KudosTransfer.objects.create(
                        emails=["founders@gitcoin.co"],
                        # For kudos, `token` is a kudos.models.Token instance.
                        kudos_token_cloned_from=coupon.token,
                        amount=coupon.token.price_in_eth,
                        comments_public=coupon.comments_to_put_in_kudos_transfer,
                        ip=ip_address,
                        github_url='',
                        from_name=coupon.sender_profile.handle,
                        from_email='',
                        from_username=coupon.sender_profile.handle,
                        network=coupon.token.contract.network,
                        from_address=kudos_owner_address,
                        receive_address=address,
                        is_for_bounty_fulfiller=False,
                        metadata={'coupon_redemption': True},
                        sender_profile=coupon.sender_profile,
                        txid=txid,
                        receive_txid=txid,
                        tx_status='pending',
                        receive_tx_status='pending',
                    )

                    coupon.num_uses_remaining -= 1
                    coupon.current_uses += 1
                    coupon.save()
            except:
                error = "Could not redeem your kudos.  Please try again soon."

    title = f"Redeem ETHDenver event kudos: *{coupon.token.humanized_name}*"
    desc = f"Thank you for joining the event! About this Kudos: {coupon.token.description}"
    params = {
        'title': title,
        'card_title': title,
        'card_desc': desc,
        'error': error,
        'avatar_url': coupon.token.img_url,
        'coupon': coupon,
        'user': request.user,
        'is_authed': request.user.is_authenticated,
        'kudos_transfer': kudos_transfer,
    }
    return TemplateResponse(request, 'ethdenver2019/receive_bulk.html', params)
