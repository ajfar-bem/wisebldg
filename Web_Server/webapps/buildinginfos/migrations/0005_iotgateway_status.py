# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-14 21:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buildinginfos', '0004_auto_20170905_1700'),
    ]

    operations = [
        migrations.AddField(
            model_name='iotgateway',
            name='status',
            field=models.TextField(blank=True, null=True),
        ),
    ]
