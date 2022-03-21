from grants.models import Grant
from grants.utils import get_clr_rounds_metadata

clr_round = get_clr_rounds_metadata()['clr_round']

# total stats

print(f"name, gitcoin url, project URL, created, category, sub-category, amount raised total, amount raised round {clr_round}, amount matched round {clr_round}, num contributors round {clr_round}, grant_sybil_score")
for grant in Grant.objects.filter(active=True):
    amount_round = 0
    try:
        amount_round = grant.clr_prediction_curve[0][1]
    except:
        pass
    print(
        "\"",
        grant.title.replace(',',''),
        "\",\"",
        "https://gitcoin.co" + grant.url,
        "\",\"",
        grant.reference_url.replace("\n",''),
        "\",\"",
        grant.created_on.strftime('%m/%d/%Y'),
        "\",\"",
        grant.grant_type,
        "\",\"",
        "::".join(grant.categories.values_list('category', flat=True)),
        "\",\"",
        grant.amount_received,
        "\",\"",
        grant.amount_received_in_round,
        "\",\"",
        amount_round,
        "\",\"",
        grant.positive_round_contributor_count,
        "\",\"",
        grant.sybil_score,
        "\"",
        )
