from django.conf import settings
from django.contrib.auth.management import create_permissions
from django.db import migrations


def apply_migration(apps, schema_editor):
    # Hack to allow addition of app default perm in migration.
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, verbosity=0)
        app_config.models_module = None

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    mod_group = Group.objects.create(name='Moderators')
    faucet_request = Permission.objects.get(codename='change_faucetrequest')
    mod_group.permissions.add(faucet_request)


def revert_migration(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get(name='Moderators').delete()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dashboard', '0096_auto_20180718_1313'),
        ('faucet', '0008_faucetrequest_profile'),
    ]

    operations = [
        migrations.RunPython(apply_migration, revert_migration),
    ]
