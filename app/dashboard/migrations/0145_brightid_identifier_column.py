from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0144_auto_20200903_1904'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='brightid_uuid',
            field=models.UUIDField(null=True),
        ),
    ]
