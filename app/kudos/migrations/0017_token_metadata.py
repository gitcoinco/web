# Generated by Django 2.2.4 on 2020-06-24 20:37

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kudos', '0016_auto_20200605_1302'),
    ]

    operations = [
        migrations.AddField(
            model_name='token',
            name='metadata',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
    ]
