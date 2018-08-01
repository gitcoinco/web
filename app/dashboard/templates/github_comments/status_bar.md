{%if status == 'open' %}
	![Open bounty]({% static 'status/open-copy.svg' %})
{%elif status == 'started' and started_work.count %}
	![Started work]({% static 'status/started-copy.svg' %})
{%elif status == 'started' and not started_work.count %}
	![Stopped work]({% static 'status/stopped-copy.svg' %})
{%elif status == 'submitted %}
	![Submitted work]({% static 'status/submitted-copy.svg' %})
{%elif status == 'done' %}
	![Approved work]({% static 'status/approved-copy.svg' %})
{% endif %}
