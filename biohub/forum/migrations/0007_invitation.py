# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-26 02:17
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum', '0006_auto_20170725_2312'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agreed', models.BooleanField(default=False)),
                ('receiver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invitations_from_receiver', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations_from_sender', to=settings.AUTH_USER_MODEL)),
                ('studio', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='forum.Studio')),
            ],
        ),
    ]
