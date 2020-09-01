from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0142_auto_20200818_0807'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='brightid_uuid',
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
    ]
