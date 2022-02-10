from grants.models import GrantQuerySet, Grant


EXPORT_FILENAME = "grants_export_for_ethelo.json"


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
        "display_data": {
            "Url": f"https://gitcoin.co{grant.url}",  # grant.url begins with `/`
            "Location": grant.region,
            "Wallet Address": grant.admin_address,
            "Twitter": "@" + grant.twitter_handle_1,
            "Grant Database Number": grant.pk,
        }
    }