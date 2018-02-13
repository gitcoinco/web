"""Define the migration from Bounty.fulfillment fields to BountyFulfillment."""
from django.db import migrations


def migrate_fulfillments(apps, schema_editor):
    """Handle the data migration from bounty fulfillment fields."""
    Bounty = apps.get_model('dashboard', 'Bounty')
    BountyFulfillment = apps.get_model('dashboard', 'BountyFulfillment')
    Profile = apps.get_model('dashboard', 'Profile')
    db_alias = schema_editor.connection.alias
    kwargs = {}

    bounties = Bounty.objects \
        .exclude(fulfiller_address__isnull=True) \
        .exclude(fulfiller_address__exact='') \
        .exclude(fulfiller_address='0x0000000000000000000000000000000000000000')

    for bounty in bounties:
        if bounty.fulfiller_address and bounty.fulfiller_github_username:
            profile = Profile.objects.filter(handle=bounty.fulfiller_github_username).first()
            if profile:
                kwargs['profile_id'] = profile.pk
            fulfillment = BountyFulfillment.objects \
                .using(db_alias) \
                .create(
                    bounty_id=bounty.pk,
                    fulfiller_address=bounty.fulfiller_address,
                    fulfiller_email=bounty.fulfiller_email,
                    fulfiller_github_username=bounty.fulfiller_github_username,
                    fulfiller_name=bounty.fulfiller_name,
                    **kwargs
                )
            bounty.fulfillments.add(fulfillment)


def rollback_migration(apps, schema_editor):
    """Handle reversing the migration steps."""
    Bounty = apps.get_model('dashboard', 'Bounty')
    db_alias = schema_editor.connection.alias

    bounties = Bounty.objects.using(db_alias) \
        .exclude(fulfiller_address__isnull=True) \
        .exclude(fulfiller_address__exact='') \
        .exclude(fulfiller_address='0x0000000000000000000000000000000000000000')

    for bounty in bounties:
        bounty.fulfillment.filter(
            fulfiller_address=bounty.fulfiller_address).delete()


class Migration(migrations.Migration):
    """Define the migration from Bounty.fulfillment fields to BountyFulfillment."""

    dependencies = [
        ('dashboard', '0040_bountyfulfillment'),
    ]

    operations = [
        migrations.RunPython(migrate_fulfillments, rollback_migration),
    ]
