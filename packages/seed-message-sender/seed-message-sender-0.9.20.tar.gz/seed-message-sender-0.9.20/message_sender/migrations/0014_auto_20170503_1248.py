# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-05-03 12:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message_sender', '0013_outbound_channel'),
    ]

    operations = [
        migrations.AddField(
            model_name='outbound',
            name='to_identity',
            field=models.CharField(blank=True, max_length=36, null=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='outbound',
            name='to_addr',
            field=models.CharField(blank=True, db_index=True, max_length=500, null=False),
        ),
        migrations.AddField(
            model_name='inbound',
            name='from_identity',
            field=models.CharField(blank=True, max_length=36, null=False, db_index=True, default=''),
        ),
        migrations.AlterField(
            model_name='inbound',
            name='from_addr',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=False),
        ),
    ]
