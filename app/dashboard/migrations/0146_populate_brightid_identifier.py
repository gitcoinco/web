from django.db import migrations, models, transaction
import uuid


def gen_uuid_0(apps, schema_editor):
    Profile = apps.get_model('dashboard', 'Profile')

    existing_uuid = []

    profiles_with_uuid = Profile.objects.filter(brightid_uuid__isnull=False)
    for profile in profiles_with_uuid:
        brightid_uuid = profile.brightid_uuid
        print(f"UUID for profile -> {profile.pk} -> {brightid_uuid}")
        while brightid_uuid in existing_uuid:
            brightid_uuid = uuid.uuid4()
            existing_uuid.append(brightid_uuid)
            profile.save()


    while Profile.objects.filter(brightid_uuid__isnull=True).exists():
        with transaction.atomic():

            for profile in Profile.objects.filter(brightid_uuid__isnull=True)[:1000]:
                brightid_uuid = uuid.uuid4()
                print(f"NO UUID for profile -> {profile.pk} -> {brightid_uuid}")
                while brightid_uuid in existing_uuid:
                    brightid_uuid = uuid.uuid4()
                    existing_uuid.append(brightid_uuid)

                profile.brightid_uuid = brightid_uuid
                profile.save()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('dashboard', '0145_brightid_identifier_column'),
    ]

    operations = [
        migrations.RunPython(gen_uuid_0, reverse_code=migrations.RunPython.noop),
    ]
