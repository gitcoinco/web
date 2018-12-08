from inbox.models import Notification
from django.contrib.auth import get_user_model

def send_notification_to_user(from_user, to_user, cta_url, cta_text, msg_html):
	new_notif = Notification(
			CTA_URL = cta_url,
			CTA_Text = cta_text,
			message_html = msg_html,
			from_user_id = get_user_model().objects.get(id=from_user),
			to_user_id = get_user_model().objects.get(id=to_user)
		)
	new_notif.save()
