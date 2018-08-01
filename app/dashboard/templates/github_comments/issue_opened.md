{% load i18n static humanize site %}
![Issue Opened]({% current_domain %}{% static "status/open-copy.svg" %})
{% if bounty.get_value_in_usdt_now %}
Funding: {{ bounty.get_natural_value|floatformat:2|intcomma }} {{ bounty.token_name }} {{ bounty.get_value_in_usdt_now|floatformat:2|intcomma }} USD @ $ {{ bounty.token_value_in_usdt_now|floatformat:2|intcomma }}/{{ bounty.token_name }}
{% endif %}
{% if bounty.permission_type == 'approval' %} [Express interest to work {% else %} [Start work {% endif %}on this issue on the Gitcoin issue details page]({{ bounty.get_absolute_url }})
{% include 'github_comments/issue_opened_marketing_footer.md' with amount_open_work=amount_open_work %}
