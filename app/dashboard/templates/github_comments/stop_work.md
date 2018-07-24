{% include 'github_comments/status_bar.md' with status=bounty.status %}
{% for profile in stopped_work %} 
[@{{ profile.handle }}]({{ profile.url }}) has stopped work on this project.
{% endfor %}
{% for profile in started_work %} 
[@{{ profile.handle }}]({{ profile.url }}) is still working on this project.
{% endfor %}
