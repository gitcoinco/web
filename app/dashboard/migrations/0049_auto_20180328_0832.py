# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def mv_forward(apps, schema_editor):

    BountyFulfillment = apps.get_model('dashboard', 'BountyFulfillment')
    for bf in BountyFulfillment.objects.filter(accepted=True):
        bf.accepted_on = bf.created_on
        bf.save()
        print(bf.pk)


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0048_auto_20180328_0829'),
    ]

    operations = [
        migrations.RunPython(
            mv_forward,
        ),
    ]
