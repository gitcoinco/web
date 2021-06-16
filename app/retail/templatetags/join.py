from django import template

register = template.Library()


@register.filter(name='join')
def join(given_list, delim=','):
    """
        Returns the list as a string joined by delimiter.
    """
    # ensure all content is provided as a string
    converted_list = [str(element) for element in given_list]

    # join by the given delimiter
    return str(delim).join(converted_list)
