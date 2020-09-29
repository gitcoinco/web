from datetime import datetime, timezone

from dashboard.models import Activity


def record_ptoken_activity(event_name, ptoken, user_profile, metadata=None, redemption=None):
    """Records activity based on ptoken changes

    Args:
        event_name (string): the event
        ptoken (ptokens.models.PersonalToken): The ptoken affected.
        user_profile (dashboard.models.Profile): The user that did the update.
        metadata (dict): Extra information.
    Raises:
        Exception: Log all exceptions that occur during fulfillment checks.

    Returns:
        dashboard.Activity: The Activity object if user_profile is present or None.
    """

    if metadata is None:
        metadata = {}
    if user_profile:
        return Activity.objects.create(
            created_on=datetime.now(),
            profile=user_profile,
            activity_type=event_name,
            redemption=redemption,
            ptoken=ptoken,
            metadata=metadata or {})
