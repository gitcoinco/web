from django.core.management.base import BaseCommand

from grants.models import Grant, GrantTag


class Command(BaseCommand):

    help = 'updates all approved grants to include the main-round tag'

    def handle(self, *args, **options):
        # main-round tag
        tag = GrantTag.objects.get(pk=62)
        grants = Grant.objects.filter(active=True, hidden=False, is_clr_eligible=True)

        print(f"adding main-round tag to {grants.count()} Grants:")

        # for every eligible grant
        for grant in grants:
            try:
                # update the tag record to include the main round tag
                grant.tags.add(tag)
                grant.save()
            except Exception as e:
                pass

        print("\n - done\n")
