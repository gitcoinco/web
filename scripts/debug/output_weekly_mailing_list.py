f = open("output.csv", "w")
import time

from marketing.models import EmailSubscriber
from marketing.utils import func_name, get_or_save_email_subscriber, should_suppress_notification_email

queryset = EmailSubscriber.objects.all()
count = queryset.count()
counter = 0
start_time = time.time()

for email in queryset:
    counter += 1
    to_email = email.email
    f_name = ''
    if email.profile:
        f_name = email.profile.data.get('name')
    if not f_name:
        f_name = ''

    if not should_suppress_notification_email(to_email, 'roundup'):
        pct_done = (round(counter / count, 2) * 100)
        if counter % 100 == 0:
            speed = counter / (time.time() - start_time)
            eta = count / speed
            print(f"{pct_done}% - {counter}/{count} ({round(speed, 1)}/s, eta:{round(eta,1)}s)")
        f.write(f"\"{f_name}\", \",\", \"{to_email}\"\n")
f.close()
