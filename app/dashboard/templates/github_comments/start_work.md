{% include 'github_comments/status_bar.md' with status=bounty.status %}
{% for started in started_work %} 
[@{{ started.profile.handle }}]({{ started.profile.url }}) {% if bounty.permission_type == 'approval' %} has been __approved__ to start work. {% else %} started work. {% endif %}
Comments: {{ started.issue_comment }}
{% endfor %}
