# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-07-03 00:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deviceinfos', '0006_supporteddevices_support_oauth'),
    ]

    operations = [
        migrations.AddField(
            model_name='supporteddevices',
            name='built_in_schedule_support',
            field=models.BooleanField(default=False),
        ),
    ]
