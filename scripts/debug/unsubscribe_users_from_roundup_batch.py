emails = ['kevin@gitcoin.co']
from marketing.models import EmailSubscriber

es = EmailSubscriber.objects.filter(email__in=emails)
print(es.count())
for ele in es:
    ele.preferences['suppression_preferences']['roundup'] = True
    ele.save()
    print(ele.preferences)
