{% load i18n static humanize %}
{% include 'github_comments/status_bar.md' with status=bounty.status %}
{% if bounty.get_value_in_usdt_now %}
Funding: {{ bounty.get_natural_value|floatformat:2|intcomma }}  {{ bounty.get_value_in_usdt_now|floatformat:2|intcomma }} USD @ $ {{ token_value_in_usdt_now|floatformat:2|intcomma }}/{{ bounty.token_name }}
{% endif %}
{% if bounty.permission_type == 'approval' %} 
[Express Interest:]({{ bounty.get_absolute_url }})
{% else %}
[Start Work:]({{ bounty.get_absolute_url }})
{% endif %} on this issue on the [Gitcoin issue details page]({{ bounty.get_absolute_url }})
{% include 'github_comments/issue_opened_marketing_footer.md' with amount_open_work=amount_open_work %}
