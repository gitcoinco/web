"""Define the migration from Bounty.current_status propery value to Bounty.status."""
from django.db import migrations
from django.utils import timezone

from dashboard.models import Bounty as BountyModel


def migrate_fulfillments(apps, schema_editor):
    """Handle the data migration from status to current_status and field.

    This is a bad example of migrations, but property hackery!
    """
    bounties = BountyModel.objects.filter(current_bounty=True).distinct()

    for bounty in bounties:
        status = BountyModel.current_status.fget(bounty)
        bounty.status = status
        bounty.save()


class Migration(migrations.Migration):
    """Define the migration from Bounty.status property to field."""

    dependencies = [
        ('dashboard', '0050_bounty_status'),
    ]

    operations = [
        migrations.RunPython(migrate_fulfillments),
    ]
