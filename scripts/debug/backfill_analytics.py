from django.utils import timezone
from marketing.models import EmailEvent, Stat

events = EmailEvent.objects.distinct('event').values_list('event',flat=True)
that_time = timezone.now()
while True:
    that_time = that_time - timezone.timedelta(hours=1)
    for event in events:
        val = EmailEvent.objects.filter(event=event, created_on__lt=that_time).count()
        Stat.objects.create(
            created_on=that_time,
            key='email_{}'.format(event),
            val=(val),
            )
        if not val:
            break
        print(that_time, val)



