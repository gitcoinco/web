{% load i18n static humanize site %}
![Issue Opened](https://oogetyboogety.github.io/gitcointestproject{% static "status/open-copy.svg" %})
--------------------

{% if bounty.get_value_in_usdt_now %}
Funding: __{{ bounty.get_natural_value|floatformat:2|intcomma }} {{ bounty.token_name }}__ (__{{ bounty.get_value_in_usdt_now|floatformat:2|intcomma }} USD__ @ $ {{ bounty.token_value_in_usdt_now|floatformat:2|intcomma }}/{{ bounty.token_name }})
{% endif %}
{% if bounty.permission_type == 'approval' %} [Express interest]({{ bounty.get_absolute_url }}) to work {% else %} [Start work]({{ bounty.get_absolute_url }}) {% endif %}on this issue on the [Gitcoin issue details page]({{ bounty.get_absolute_url }})
{% include 'github_comments/issue_opened_marketing_footer.md' with amount_open_work=amount_open_work %}
