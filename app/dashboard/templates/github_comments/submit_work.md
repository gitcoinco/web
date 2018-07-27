{% include 'github_comments/status_bar.md' with status=bounty.status %}
{% for profile in fulfillments %}
  [@{{ profile.handle }}]({{ profile.url }}) has __submitted work__ for this project.
{% endfor %}

