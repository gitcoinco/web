from grants.models import *

# total stats

print("name, gitcoin url, project URL, created, category, sub-category, amount raised total, amount raised round 5, amount matched round 5, num contributors round 5, github_url")
for grant in Grant.objects.filter(active=True):
    amount_round = 0
    try: 
        amount_round = grant.clr_prediction_curve[0][1]
    except:
        pass
    print(
        grant.title.replace(',',''),
        ",",
        "https://gitcoin.co" + grant.url,
        ",",
        grant.reference_url.replace("\n",''),
        ",",
        grant.created_on.strftime('%m/%d/%Y'),
        ",",
        grant.grant_type,
        ",",
        "::".join(grant.categories.values_list('category', flat=True)),
        ",",
        grant.amount_received,
        ",",
        grant.amount_received_in_round,
        ",",
        amount_round,
        ",",
        grant.positive_round_contributor_count,
        ",",
        )
