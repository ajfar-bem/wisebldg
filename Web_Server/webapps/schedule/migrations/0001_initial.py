# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-17 19:38
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('buildinginfos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Holiday',
            fields=[
                ('date', models.DateField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=50)),
                ('building', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='buildinginfos.BuildingInfo')),
            ],
            options={
                'db_table': 'holiday',
            },
        ),
        migrations.CreateModel(
            name='schedule_data',
            fields=[
                ('agent_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('schedule', django.contrib.postgres.fields.jsonb.JSONField(default={})),
            ],
            options={
                'db_table': 'schedule_data',
            },
        ),
    ]
