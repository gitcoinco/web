from inbox.models import Notification


def send_notification_to_user(from_user, to_user, cta_url, cta_text, msg_html):
    """Helper method to create a new notification."""
    Notification.objects.create(
        cta_url=cta_url,
        cta_text=cta_text,
        message_html=msg_html,
        from_user=from_user,
        to_user=to_user
    )
