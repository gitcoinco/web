# Generated by Django 2.2.4 on 2020-06-05 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0118_auto_20200605_1302'),
    ]

    operations = [
        migrations.AddField(
            model_name='hackathonevent',
            name='short_code',
            field=models.CharField(default='', help_text='used in the chat for better channel grouping', max_length=5),
        ),
        migrations.AddField(
            model_name='hackathonproject',
            name='winner',
            field=models.BooleanField(default=False),
        ),
    ]
