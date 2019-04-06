# Generated by Django 2.1.7 on 2019-04-06 01:56

from django.db import migrations

def category_char_field_to_array(apps, schema_editor):
    EmailEvent = apps.get_model('marketing', 'EmailEvent')
    for email_event in EmailEvent.objects.all():
        categories_char = email_event.category
        categories_char = categories_char.strip('[]')
        categories_list = [category.strip("''") for category in categories_char.split(',')]
        email_event.categories = categories_list
        email_event.save()

class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0003_emailevent_categories'),
    ]

    operations = [
        migrations.RunPython(category_char_field_to_array),
    ]
