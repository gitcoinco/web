from django.http import Http404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse

from external_bounties.models import ExternalBounty, ExternalBountyForm
from marketing.mails import new_external_bounty


def external_bounties_index(request):
    """Handle External Bounties index page."""

    tags = []
    external_bounties_results = []
    bounties = ExternalBounty.objects.filter(active=True)
    for external_bounty_result in bounties:
        external_bounty = {
            "created_on": external_bounty_result.created_on,
            "avatar": external_bounty_result.avatar,
            "title": external_bounty_result.title,
            "source": external_bounty_result.source_project,
            "crypto_price": external_bounty_result.amount,
            "fiat_price": external_bounty_result.fiat_price,
            "crypto_label": external_bounty_result.amount_denomination,
            "tags": external_bounty_result.tags,
            "url": external_bounty_result.url,
        }
        tags = tags + external_bounty_result.tags
        external_bounties_results.append(external_bounty)
        categories = list(set(tags))
        categories.sort()

    params = {
        'active': 'offchain',
        'title': 'Offchain Bounty Explorer',
        'bounties': external_bounties_results,
        'categories': categories,
    }
    return TemplateResponse(request, 'external_bounties.html', params)


def external_bounties_new(request):
    params = {
        'active': 'offchain',
        'title': 'New Offchain Bounty',
        'formset': ExternalBountyForm,
    }

    if request.POST:
        new_eb = ExternalBountyForm(request.POST)
        new_eb.github_handle = request.session.get('handle')
        new_eb.save()
        new_external_bounty()
        params['msg'] = "An email has been sent to an administrator to approve your submission"

    return TemplateResponse(request, 'external_bounties_new.html', params)


def external_bounties_show(request, issuenum, slug):
    """Handle Dummy External Bounties show page."""

    print('************')
    print(issuenum)
    if issuenum == '':
        return external_bounties_index(request)

    try:
        bounty = ExternalBounty.objects.get(pk=issuenum, active=True)
    except:
        raise Http404

    external_bounty = {}
    external_bounty_result = bounty
    external_bounty['created_on'] = external_bounty_result.created_on
    external_bounty['title'] = external_bounty_result.title
    external_bounty['crypto_price'] = external_bounty_result.amount
    external_bounty['crypto_label'] = external_bounty_result.amount_denomination
    external_bounty['fiat_price'] = external_bounty_result.amount
    external_bounty['source'] = external_bounty_result.source_project
    external_bounty['content'] = external_bounty_result.description
    external_bounty['action_url'] = external_bounty_result.action_url
    external_bounty['avatar'] = external_bounty_result.avatar
    external_bounty['fiat_price'] = external_bounty_result.fiat_price

    params = {
        'active': 'offchain',
        'title': 'Offchain Bounty Explorer',
        "bounty": external_bounty,
    }
    return TemplateResponse(request, 'external_bounties_show.html', params)
