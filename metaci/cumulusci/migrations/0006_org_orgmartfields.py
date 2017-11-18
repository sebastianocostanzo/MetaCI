# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-17 00:58
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('repository', '0002_auto_20171031_2037'),
        ('cumulusci', '0005_scratchorginstance_delete_error'),
    ]

    operations = [
        migrations.AddField(
            model_name='org',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='org',
            name='org_id',
            field=models.CharField(blank=True, max_length=18, null=True),
        ),
        migrations.AddField(
            model_name='org',
            name='org_type',
            field=models.CharField(choices=[(b'SCRATCH', b'Scratch Org Definition'), (b'PACKAGING', b'Packaging Org'), (b'UNMANAGED', b'Persistent Test Org (Unmanaged)'), (b'BETA', b'Persistent Test Org (Beta Package)'), (b'PRODUCTION', b'Persistent Test Org (Production Package)'), (b'TRIAL', b'Trial Source Org (Production Package'), (b'ADMIN', b'Administrative Org (no package)')], default=b'PRODUCTION', max_length=50),
        ),
        migrations.AddField(
            model_name='org',
            name='push_schedule',
            field=models.CharField(blank=True, choices=[(b'QA', b'QA Orgs')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='org',
            name='supertype',
            field=models.CharField(choices=[(b'CI', b'CI Test Org'), (b'REGISTERED', b'Registered Org')], default=b'CI', max_length=50),
        ),
        migrations.AddField(
            model_name='org',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='registered_orgs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='org',
            unique_together=set([('repo', 'name')]),
        ),
    ]
