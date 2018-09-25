from django.conf import settings
from django.db import migrations


def apply_migration(apps, schema_editor):
    pass


def revert_migration(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dashboard', '0100_auto_20180726_1254'),
        ('faucet', '0011_auto_20180723_1315'),
    ]

    operations = [
        migrations.RunPython(apply_migration, revert_migration),
    ]
