{% load static %}
![Start work](https://oogetyboogety.github.io/gitcointestproject{% static 'status/started-copy.svg' %})
--------------------

{% for started in started_work %} 
[@{{ started.profile.handle }}]({{ started.profile.url }}){% if bounty.permission_type == 'approval' %} has been __approved__ to start work on this project. {% else %} has __started work__ on this project. {% endif %}
Comments: {{ started.issue_comment }}
{% endfor %}
