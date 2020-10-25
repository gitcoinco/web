from django.db import migrations, transaction
import uuid


def gen_uuid_0(apps, schema_editor):
    Profile = apps.get_model('dashboard', 'Profile')

    existing_uuid = []

    profiles_with_uuid = Profile.objects.filter(idena_token__isnull=False)
    for profile in profiles_with_uuid:
        idena_token = profile.brightid_uuid
        print(f"UUID for profile -> {profile.pk} -> {idena_token}")
        while idena_token in existing_uuid:
            idena_token = uuid.uuid4()
            existing_uuid.append(idena_token)

    while Profile.objects.filter(idena_token__isnull=True).exists():
        with transaction.atomic():

            for profile in Profile.objects.filter(idena_token__isnull=True)[:1000]:
                idena_token = uuid.uuid4()
                print(f"NO UUID for profile -> {profile.pk} -> {idena_token}")
                while idena_token in existing_uuid:
                    idena_token = uuid.uuid4()
                    existing_uuid.append(idena_token)

                profile.idena_token = idena_token
                profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0154_profile_idena_address'),
    ]

    operations = [
        migrations.RunPython(gen_uuid_0, reverse_code=migrations.RunPython.noop),
    ]
