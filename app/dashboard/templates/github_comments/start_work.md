{% include 'github_comments/status_bar.md' with status=bounty.status %}
{% for profile in started_work %} 
[@{{ profile.handle }}]({{ profile.url }}) {% if bounty.permission_type == 'approval' %} has been approved to start work. {% else %} started work. {% endif %}
{% endfor %}
