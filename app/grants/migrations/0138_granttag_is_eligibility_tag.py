# Generated by Django 2.2.24 on 2022-03-04 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grants', '0137_auto_20220214_0629'),
    ]

    operations = [
        migrations.AddField(
            model_name='granttag',
            name='is_eligibility_tag',
            field=models.BooleanField(default=False, help_text='Is this tag a eligibility'),
        ),
    ]
