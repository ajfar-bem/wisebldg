# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-18 16:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buildinginfos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buildinginfo',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='buildinginfo',
            name='zip_code',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='zoneinfo',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterModelTable(
            name='buildinginfo',
            table='building_info',
        ),
        migrations.AlterModelTable(
            name='iotgateway',
            table='IOT_gateway',
        ),
    ]
