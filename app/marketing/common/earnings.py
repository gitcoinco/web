import io
import csv
import logging

from django.conf import settings

from marketing.mails import send_mail
from retail.emails import render_export_data_email, render_export_data_email_failed

logger = logging.getLogger(__name__)

def export_earnings(export_type, profile):
    earnings = profile.earnings if export_type == 'earnings' else profile.sent_earnings
    earnings = earnings.filter(network='mainnet').order_by('-created_on')
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(['ID', 'Date', 'From', 'From Location', 'To', 'To Location', 'Type', 'Value In USD', 'TXID', 'Token Name', 'Token Value', 'URL'])
    for earning in earnings:
        writer.writerow([
            earning.pk,
            earning.created_on.strftime("%Y-%m-%dT%H:00:00"),
            earning.from_profile.handle if earning.from_profile else '*',
            earning.from_profile.data.get('location', 'Unknown') if earning.from_profile else 'Unknown',
            earning.to_profile.handle,
            earning.to_profile.data.get('location', 'Unknown'),
            earning.source_type_human,
            earning.value_usd,
            earning.txid,
            earning.token_name,
            earning.token_value,
            earning.url,
        ])

    return buf


def send_csv(data, user_profile):
    to_email = user_profile.user.email
    from_email = settings.CONTACT_EMAIL
    html, text, subject = render_export_data_email(user_profile=user_profile)
    send_mail(
        from_email,
        to_email,
        subject,
        text,
        html,
        from_name=f"@{user_profile.handle}",
        categories=['transactional'],
        csv=data
    )


def send_download_failure_email(user_profile):
    to_email = user_profile.user.email
    from_email = settings.CONTACT_EMAIL
    html, text, subject = render_export_data_email_failed(user_profile=user_profile)
    send_mail(
        from_email,
        to_email,
        subject,
        text,
        html,
        from_name=f"@{user_profile.handle}",
        categories=['transactional'],
    )
