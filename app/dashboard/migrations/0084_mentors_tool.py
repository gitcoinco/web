# Generated by Django 2.0.3 on 2018-04-25 18:34

from django.db import migrations

def update(apps, schema_editor):
    Tool = apps.get_model('dashboard', 'Tool')

    Tool.objects.filter(name='Mentorship Matcher').update(category='AL', link='', url_name="mentors", link_copy="Try It" )

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0083_merge_20180601_1945'),
    ]

    operations = [
        migrations.RunPython(update)
    ]
