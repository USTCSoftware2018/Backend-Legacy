# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-19 07:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0002_auto_20170919_1517'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='experience',
            options={'ordering': ('-pub_time', 'id')},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_time']},
        ),
    ]
