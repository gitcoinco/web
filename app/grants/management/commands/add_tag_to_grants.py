from django.core.management.base import BaseCommand

from grants.models import Grant, GrantTag

class Command(BaseCommand):
    help = 'Add grant tag to all grants in a certain grant type'

    def add_arguments(self, parser):
        parser.add_argument('current_type_pk', type=str, default="")
        parser.add_argument('new_tag_name', type=str, default="")

    def handle(self, *args, **options):
        current_type_pk = options['current_type_pk']
        new_tag_name = options['new_tag_name']

        grants_to_modify = Grant.objects.filter(grant_type=current_type_pk, active=True)
        tag_to_add = GrantTag.objects.get(name=new_tag_name)
        for grant in grants_to_modify:
            #if tag_to_add not in grant.tags:
            try:
                grant.tags.add(tag_to_add)
            except Exception as e:
                pass
        grant.save()
