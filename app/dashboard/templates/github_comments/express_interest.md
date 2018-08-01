![Express Interest]({% static "status/open-copy.svg" %}
{% if bounty.permission_type == 'approval' %} 
{% for interest in interested %} 
[@{{ interest.profile.handle }}]({{ interest.profile.url }}) has __expressed interest__ in this project.
	{% if interest.approve_link or interest.reject_link %}
[@{{ bounty.bounty_owner_profile.handle }},]({{ bounty.bounty_owner_profile.url }}) [Approve Worker]({{ interest.approve_link }}) | [Reject Worker]({{ interest.reject_link }})
	{% endif %}
{% endfor %}
{% endif %}
