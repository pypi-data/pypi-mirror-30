# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-12 11:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0019_restructure_org_config'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='org',
            name='api_token',
        ),
    ]
