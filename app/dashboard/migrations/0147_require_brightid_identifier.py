from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0146_populate_brightid_identifier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='brightid_uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
