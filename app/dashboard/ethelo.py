from grants.models import GrantQuerySet, Grant


def get_grants_from_database(start_grant_number: int, end_grant_number: int=None) -> dict:
    """Query the grants database and return a JSONify-able dict that can be uploaded into ethelo.

    Args:
        start_grant_number (int): The index of the starting grant.
        end_grant_number (int, optional): The index of the ending grant. If None, all grants after `start_grant_number` 
            will be included. Defaults to None.

    Returns:
        dict: The returned dict will be JSONify-able.
    """

    query = GrantQuerySet(Grant)
    if end_grant_number is None:
        end_grant_number = query.count()
    pk_list = list(range(start_grant_number, end_grant_number + 1))
    query.filter(pk__in=pk_list)

    return {"options": [_format_grant(grant) for grant in query]}


def _format_grant(grant: Grant) -> dict:
    """Format a grant into a dict compatible with ethelo.

    Args:
        grant (Grant): Grant to be formatted.

    Returns:
        dict: JSONify-able grant dictionary.
    """

    if len(grant.description_rich) > 0:
        info = grant.description_rich
    else:
        info = grant.description

    return {
        "slug": f"grant_{grant.pk}",
        "title": grant.title,
        "info": info,
        "optional_category_slug": "TODO:OPTION_CATEGORY_SLUG",
        "display_data": {
            "url": grant.url,
            "location": grant.region,
            "wallet_address": "see grant URL",  # TODO: there are so many wallet addresses..... which one do we display?
            "twitters": [grant.twitter_handle_1, grant.twitter_handle_2],
            "grant_number": grant.pk,
        }
    }