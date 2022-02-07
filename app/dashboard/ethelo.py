from grants.models import GrantQuerySet, Grant


def get_grants_from_database(start_grant_number: int, end_grant_number: int=None) -> list:
    # TODO: docstring

    query = GrantQuerySet(Grant)
    print(query)

    strs = [str(grant) for grant in query]
    return {"grants": strs}