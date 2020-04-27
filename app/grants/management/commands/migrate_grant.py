from django.conf import settings
from django.core.management.base import BaseCommand

from grants.models import Grant


class Command(BaseCommand):

    help = 'migrates the activity on one grant to another'

    def add_arguments(self, parser):

        parser.add_argument('old_grant_pk', type=int)
        parser.add_argument('new_grant_pk', type=int)

    def handle(self, *args, **options):

        old_grant_pk = options['old_grant_pk']
        new_grant_pk = options['new_grant_pk']

        old_grant = Grant.objects.get(pk=old_grant_pk)
        new_grant = Grant.objects.get(pk=new_grant_pk)

        print(f'========= \n MIGRATING ACTIVITY FROM ({old_grant.pk}) {old_grant.title} TO ({new_grant.pk}) {new_grant.title} \n========')

        for sub in old_grant.subscriptions.all():
            sub.grant = new_grant
            sub.save()

        for obj in old_grant.phantom_funding.all():
            obj.grant = new_grant
            obj.save()

        for obj in old_grant.activities.all():
            obj.grant = new_grant
            obj.save()

        for obj in old_grant.clr_matches.all():
            obj.grant = new_grant
            obj.save()

        old_grant.hidden = True
        old_grant.link_to_new_grant = new_grant

        old_grant.save()
        new_grant.save()

        print(f'======== \n ACTIVITIES MIGRATED. \n GRANT {old_grant.pk} is inactive & linked to GRANT {new_grant.pk} \n========')
