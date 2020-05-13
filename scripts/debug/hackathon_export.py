from dashboard.models import Bounty, HackathonEvent

# bounty data export script for electric capital
print("hackathon name, start date, end date, bounty_created, bounty url, bounty title, bounty amount, bounty token, contributors, github_issue, fulfiller_name, fulfiller_pr")
for bounty in Bounty.objects.current().filter(idx_status='done'):
      for bf in bounty.fulfillments.all():
            he = bounty.event
            print(
            he.name.replace(",", '') if he else "",
            ",",
            he.start_date.strftime('%m/%d/%Y') if he else "",
            ",",
            he.end_date.strftime('%m/%d/%Y') if he else "",
            ",",
            bounty.web3_created.strftime('%m/%d/%Y'),
            ",",
            bounty.url.replace(",", ''),
            ",",
            bounty.title.replace(",", ''),
            ",",
            bounty.value_true,
            ",",
            bounty.token_name,
            ",",
            bounty.interested.count(),
            ",",
            f"https://github.com/{bounty.org_name}/{bounty.github_repo_name}",
            ",",
            bf.fulfiller_github_username,
            ",",
            bf.fulfiller_github_url,
            )
