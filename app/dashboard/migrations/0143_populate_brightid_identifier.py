from django.db import migrations, models
import uuid

def gen_uuid(apps, schema_editor):
    Profile = apps.get_model('dashboard', 'Profile')
    for row in Profile.objects.all():
        row.brightid_uuid = uuid.uuid4()
        row.save(update_fields=['brightid_uuid'])

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0142_brightid_identifier_column'),
    ]

    operations = [
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
    ]
