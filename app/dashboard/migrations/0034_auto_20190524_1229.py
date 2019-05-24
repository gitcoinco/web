# Generated by Django 2.1.7 on 2019-05-24 12:29

from django.db import migrations, models
from dashboard.models import Profile

def forwards_func(apps, schema_editor):
    for profile in list(Profile.objects.all()):
        profile.calculate_and_save_persona()

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0033_bounty_bounty_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='persona_is_funder',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='persona_is_hunter',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(forwards_func),
    ]
