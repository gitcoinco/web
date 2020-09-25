from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0148_add_brightid_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_twitter_verified',
            field=models.BooleanField(default=False)
        ),
        migrations.AddField(
            model_name='profile',
            name='twitter_handle',
            field=models.CharField(blank=True, null=True, max_length=15)
        ),
    ]
