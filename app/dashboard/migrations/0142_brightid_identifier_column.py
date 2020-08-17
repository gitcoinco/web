from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0141_auto_20200813_1219'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='brightid_uuid',
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
    ]
