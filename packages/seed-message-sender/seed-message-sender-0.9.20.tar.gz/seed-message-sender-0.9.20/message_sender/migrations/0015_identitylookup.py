# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-05-08 14:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message_sender', '0014_auto_20170503_1248'),
    ]

    operations = [
        migrations.CreateModel(
            name='IdentityLookup',
            fields=[
                ('msisdn', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('identity', models.CharField(blank=False, max_length=36, null=False)),
            ],
        ),
    ]
