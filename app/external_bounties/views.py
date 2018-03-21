from django.template.response import TemplateResponse


def external_bounties_index(request):
    """Handle Dummy External Bounties index page."""

    bounties = [
        {
            "title": "Add Web3 1.0 Support",
            "source": "www.google.com",
            "crypto_price": 0.3,
            "fiat_price": 337.88,
            "crypto_label": "ETH",
            "tags": ["javascript", "python", "eth"],
        },
        {
            "title": "Simulate proposal execution and display execution results",
            "source": "gitcoin.com",
            "crypto_price": 1,
            "fiat_price": 23.23,
            "crypto_label": "BTC",
            "tags": ["ruby", "js", "btc"]
        },
        {
            "title": "Build out Market contract explorer",
            "crypto_price": 22,
            "fiat_price": 203.23,
            "crypto_label": "LTC",
            "tags": ["ruby on rails", "ios", "mobile", "design"]
        },
    ]

    categories = ["Blockchain", "Web Development", "Design", "Browser Extension", "Beginner"]

    params = {
        'active': 'dashboard',
        'title': 'Offchain Bounty Explorer',
        'bounties': bounties,
        'categories': categories
    }
    return TemplateResponse(request, 'external_bounties.html', params)


def external_bounties_show(request, issuenum):
    print('************')
    print(issuenum)
    if issuenum == '':
        return external_bounties_index(request)

    """Handle Dummy External Bounties show page."""
    bounty = {
        "title": "Simulate proposal execution and display execution results",
        "crypto_price": 0.5,
        "crypto_label": "ETH",
        "fiat_price": 339.34,
        "source": "gitcoin.co",
        "content": "Lorem"
    }
    params = {
        'active': 'dashboard',
        'title': 'Offchain Bounty Explorer',
        "bounty": bounty,
    }
    return TemplateResponse(request, 'external_bounties_show.html', params)
