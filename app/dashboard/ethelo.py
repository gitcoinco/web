from grants.models import Grant, GrantQuerySet

EXPORT_FILENAME = "grants_export_for_ethelo.json"


def get_grants_from_database(start_grant_number: int, end_grant_number: int=None, inactive_grants_only: bool=True) -> dict:
    """Query the grants database and return a JSONify-able dict that can be uploaded into ethelo.

    Args:
        start_grant_number (int): The index of the starting grant.
        end_grant_number (int, optional): The index of the ending grant. If None, all grants after `start_grant_number` 
            will be included. Defaults to None.
        inactive_grants_only (bool): If True, only grants that have not been activated by admins yet will be exported.

    Returns:
        dict: The returned dict will be JSONify-able.
    """

    query = GrantQuerySet(Grant)

    if end_grant_number is None:
        end_grant_number = query.count()

    pk_list = list(range(start_grant_number, end_grant_number + 1))
    query.filter(pk__in=pk_list)

    grants = [
        _format_grant(grant)
        for grant in query
        if not inactive_grants_only or not grant.active
    ]

    return {"options": grants}


def _format_grant(grant: Grant) -> dict:
    """Format a grant into a dict compatible with ethelo.

    Args:
        grant (Grant): Grant to be formatted.

    Returns:
        dict: JSONify-able grant dictionary.
    """

    tags = list(grant.tags.all().values_list("name", flat=True))

    return {
        "slug": f"grant_{grant.pk}",
        "title": grant.title,
        "info": grant.description_rich,  # NOTE: grant.description is just a weird stringified JSON of the rich description
        "display_data": {
            "Status": _get_status(grant),
            "Grant Url": f'https://gitcoin.co{grant.url}',
            "Github Project Url": grant.github_project_url,
            "Location": grant.region,
            "Wallet Address": grant.admin_address,
            "Twitter": f'@{grant.twitter_handle_1}',
            "Creator Handle": grant.admin_profile.handle,
            "Database Number": grant.pk,
            "Tags": tags,
        },
    }


def _get_status(grant: Grant) -> str:
    return "Approved" if grant.active else "Unapproved"
