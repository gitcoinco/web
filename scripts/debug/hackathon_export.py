from dashboard.models import HackathonEvent, Bounty

# total stats

print("hackathon name, start date, end date, bounty url, bounty title, bounty amount, bounty token, contributors, github_issue")
for he in HackathonEvent.objects.order_by('start_date'):
    for bounty in Bounty.objects.filter(event=he):
        print(
            he.name,
            ",",
            he.start_date.strftime('%m/%d/%Y'),
            ",",
            he.end_date.strftime('%m/%d/%Y'),
            ",",
            bounty.url,
            ",",
            bounty.title,
            ",",
            bounty.value_true,
            ",",
            bounty.token_name,
            ",",
            bounty.interested.count(),
            ",",
            f"https://github.com/{bounty.org_name}/{bounty.github_repo_name}",
            )
