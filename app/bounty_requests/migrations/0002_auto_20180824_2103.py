# Generated by Django 2.1 on 2018-08-24 21:03

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bounty_requests', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bountyrequest',
            name='amount',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(1.0)]),
        ),
    ]
