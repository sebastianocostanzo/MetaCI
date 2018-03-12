# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-03-02 22:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plan', '0013_create_default_plans'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plan',
            name='type',
            field=models.CharField(choices=[('manual', 'Manual'), ('commit', 'Commit'), ('tag', 'Tag'), ('org', 'Org Request')], max_length=8),
        ),
    ]
