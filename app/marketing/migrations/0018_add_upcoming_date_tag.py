from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0017_auto_20200903_1904'),
    ]

    operations = [
        migrations.AddField(
            model_name='UpcomingDate',
            name='context_tag',
            field=models.TextField(default='', max_length=255),
        ),
    ]
