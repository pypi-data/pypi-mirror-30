# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-03-23 14:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message_sender', '0008_auto_20170323_1042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inbound',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
