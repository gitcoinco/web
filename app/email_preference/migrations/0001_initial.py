# Generated by Django 2.2.24 on 2022-08-17 12:41

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import economy.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailPreferenceLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.PositiveIntegerField(blank=True, null=True)),
                ('destination', models.CharField(default='hubspot', max_length=255)),
                ('event_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('response_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('created_on', models.DateTimeField(db_index=True, default=economy.models.get_time)),
                ('modified_on', models.DateTimeField(default=economy.models.get_time)),
                ('processed_on', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
