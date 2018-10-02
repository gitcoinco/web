import json
import logging

logger = logging.getLogger(__name__)

from django.template.response import TemplateResponse

from marketing.models import Keyword
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from web3 import HTTPProvider, Web3
from .models import Grant, Subscription

# web3.py instance
w3 = Web3(HTTPProvider(settings.WEB3_HTTP_PROVIDER))

def grants(request):
    """Handle grants explorer."""
    grants = Grant.objects.all()

    params = {
        'active': 'dashboard',
        'title': 'Grants Explorer',
        'grants': grants,
        'keywords': json.dumps([str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)]),
    }
    return TemplateResponse(request, 'grants/index.html', params)


def grant_show(request, grant_id):
    grant = Grant.objects.get(pk=grant_id)

    params = {
        'active': 'dashboard',
        'title': 'Grant Show',
        'grant': grant,
        'keywords': json.dumps([str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)]),
    }
    return TemplateResponse(request, 'grants/show.html', params)

def new_grant(request):
    """Handle new grant."""
    profile_id = request.session.get('profile_id')
    profile = request.user.profile if request.user.is_authenticated else None

    print('request', request.POST)

    if request.method == "POST":
        grant = Grant()

        print('request', request.POST)

        grant.title = request.POST.get('input-name')
        grant.description = request.POST.get('description')
        grant.reference_url = request.POST.get('reference_url')
        grant.image_url = request.POST.get('input-image')
        grant.admin_address = request.POST.get('admin_address')
        grant.frequency = request.POST.get('frequency')
        grant.token_address = request.POST.get('denomination')
        grant.amount_goal = request.POST.get('amount_goal')
        grant.transaction_hash = request.POST.get('transaction_hash')
        grant.contract_address = request.POST.get('contract_address')
        grant.network = request.POST.get('network')

        grant.admin_profile = profile
        # grant.teamMemberProfiles = Need to do a profile search based on enetered emails

        grant.save()

        return redirect(f'/grants/{grant.pk}')

    else:
        grant = {}

    params = {
        'active': 'grants',
        'title': 'New Grant',
        'grant': grant,
        'keywords': json.dumps([str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)]),
    }

    return TemplateResponse(request, 'grants/new.html', params)




def fund_grant(request, grant_id):
    """Handle grant funding."""
    # import ipdb; ipdb.set_trace()
    grant = Grant.objects.get(pk=grant_id)

    profile_id = request.session.get('profile_id')
    profile = request.user.profile if request.user.is_authenticated else None

    print("this is the username:", profile)
    print("this is the grant instance", grant)
    print("this is the web3 instance", w3.eth.account)

    # make sure a user can only create one subscription per grant

    if request.method == "POST":
        subscription = Subscription()


        # subscriptionHash and ContributorSignature will be given from smartcontracts and web3
        # subscription.subscriptionHash = request.POST.get('input-name')
        # subscription.contributorSignature = request.POST.get('description')
        # Address will come from web3 instance
        # subscription.contributorAddress = request.POST.get('reference_url')
        subscription.amount_per_period = request.POST.get('amount_per_period')
        # subscription.tokenAddress = request.POST.get('denomination')
        subscription.gas_price = request.POST.get('gas_price')
        # network will come from web3 instance
        # subscription.network = request.POST.get('amount_goal')
        subscription.contributor_profile = profile
        subscription.grant = grant


        subscription.save()
    else:
        subscription = {}


    params = {
        'active': 'dashboard',
        'title': 'Fund Grant',
        'subscription': subscription,
        'grant': grant,
        'keywords': json.dumps([str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)]),
    }


    return TemplateResponse(request, 'grants/fund.html', params)

def cancel_subscription(request, subscription_id):
    """Handle Cancelation of grant funding"""
    profile_id = request.session.get('profile_id')
    profile = request.user.profile if request.user.is_authenticated else None

    subscription = Subscription.objects.get(pk=subscription_id)
    grant = subscription.grant

    print("this is the subscription:", subscription.pk)
    print("this is the grant:", grant)

    if request.method == "POST":

        subscription.status = False

        subscription.save()
    # else:
        # subscription = {}


    params = {
        'title': 'Fund Grant',
        'subscription': subscription,
        'grant': grant,
        'keywords': json.dumps([str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)]),
    }

    return TemplateResponse(request, 'grants/cancel.html', params)
