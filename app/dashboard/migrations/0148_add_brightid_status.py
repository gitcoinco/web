from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0147_require_brightid_identifier'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_brightid_verified',
            field=models.BooleanField(default=False)
        ),
    ]
