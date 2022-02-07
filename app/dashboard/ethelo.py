from grants.models import GrantQuerySet


def get_grants_dict(start_grant_number: int, end_grant_number: int=None) -> dict:
    # TODO: docstring

    query = GrantQuerySet().all()

    strs = [str(grant) for grant in query]
    return {"grants": strs}