{% load static %}
![Submitted Work](https://oogetyboogety.github.io/gitcointestproject{% static "status/submitted-copy.svg" %})
--------------------

{% for profile in fulfillments %}
  [@{{ profile.handle }}]({{ profile.url }}) has __submitted work__ for this project.
{% endfor %}

