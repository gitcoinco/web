{% include 'github_comments/status_bar.md' with status=bounty.status %}
{% for profile in fulfillments %}
  [@{{ profile.handle }}]({{ profile.url }}) has _submitted work_ for this project.
{% endfor %}

