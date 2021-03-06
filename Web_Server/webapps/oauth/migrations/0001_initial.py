# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-28 18:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('buildinginfos', '0006_auto_20170914_2305'),
    ]

    operations = [
        migrations.CreateModel(
            name='oauthToken',
            fields=[
                ('token_id', models.AutoField(primary_key=True, serialize=False)),
                ('service_provider', models.CharField(max_length=100)),
                ('token', models.CharField(max_length=1000)),
                ('obtained_time', models.DateTimeField()),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='buildinginfos.BuildingInfo')),
            ],
            options={
                'db_table': 'oauth_token',
            },
        ),
    ]
