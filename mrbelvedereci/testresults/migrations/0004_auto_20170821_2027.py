# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-21 20:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('build', '0011_auto_20170814_1739_squashed_0013_auto_20170814_1745'),
        ('testresults', '0003_auto_20170814_2352'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestSuiteRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suite_name', models.CharField(db_index=True, max_length=255)),
                ('kind', models.CharField(choices=[(b'apex', b'Apex'), (b'browser', b'Browser'), (b'other', b'Other')], default='Other', max_length=25)),
                ('tests_total', models.IntegerField(blank=True, null=True)),
                ('tests_pass', models.IntegerField(blank=True, null=True)),
                ('tests_fail', models.IntegerField(blank=True, null=True)),
                ('build_flow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_suite_runs', to='build.BuildFlow')),
            ],
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='callouts_allowed',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='callouts_percent',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='callouts_used',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='cpu_time_allowed',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='cpu_time_percent',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='cpu_time_used',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='dml_rows_allowed',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='dml_rows_percent',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='dml_rows_used',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='dml_statements_allowed',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='dml_statements_percent',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='dml_statements_used',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='email_invocations_allowed',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='email_invocations_percent',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='email_invocations_used',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='future_calls_allowed',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='future_calls_percent',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='future_calls_used',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='heap_size_allowed',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='heap_size_percent',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='heap_size_used',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='mobile_apex_push_allowed',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='mobile_apex_push_percent',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='mobile_apex_push_used',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='query_rows_allowed',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='query_rows_percent',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='query_rows_used',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='queueable_jobs_allowed',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='queueable_jobs_percent',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='queueable_jobs_used',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='soql_queries_allowed',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='soql_queries_percent',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='soql_queries_used',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='sosl_queries_allowed',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='sosl_queries_percent',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='sosl_queries_used',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='worst_limit_nontest',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='worst_limit_nontest_percent',
        ),
        migrations.AddField(
            model_name='testresult',
            name='test_suite_run',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='test_results', to='testresults.TestSuiteRun'),
        ),
    ]
