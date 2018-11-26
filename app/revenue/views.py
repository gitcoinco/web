from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from ratelimit.decorators import ratelimit
from retail.helpers import get_ip
from revenue.models import DigitalGoodPurchase
from web3 import Web3

# Create your views here.

@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
@csrf_exempt
def new_attestation(request):

    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 403,
            'message': "Not Authorized",
            }, status=403)

    if request.POST:
        to_user = 'gitcoinbot'
        already_exists = DigitalGoodPurchase.objects.filter(txid__iexact=request.GET.get('txid')).exists()
        if not already_exists:
            metadata = {
                'type': request.POST.get('type'),
                'option': request.POST.get('option'),
                'value': request.POST.get('value'),
            }
            dgp = DigitalGoodPurchase.objects.create(
                emails=[request.user.email],
                # For kudos, `token` is a kudos.models.Token instance.
                amount=request.POST.get('amount'),
                ip=get_ip(request),
                github_url='',
                from_name=request.user.username,
                from_email='',
                from_username=request.user.username,
                username=to_user,
                network=request.POST.get('network'),
                from_address=request.POST.get('from_address'),
                receive_address=request.POST.get('to_address'),
                metadata=metadata,
                txid=request.POST.get('txid'),
                receive_txid=request.POST.get('txid'),
                tx_status='pending',
                receive_tx_status='pending',
                purchase=metadata,
                purchase_expires=timezone.now() + timezone.timedelta(days=(999 * 365)),
            )
            dgp.update_tx_status()
            dgp.save()

    return JsonResponse({
        'status': 200,
        'message': "OK",
        }, status=200)
