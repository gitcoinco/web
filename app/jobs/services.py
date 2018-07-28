import bleach


def clean_html_data(html_data, allowed_tags=['strong', 'em']):
    html_data = bleach.clean(html_data, tags=allowed_tags)
    return html_data
