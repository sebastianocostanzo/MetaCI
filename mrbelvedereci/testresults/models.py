from __future__ import unicode_literals

from collections import OrderedDict
from django.db import models
from mrbelvedereci.testresults.choices import OUTCOME_CHOICES, TEST_SUITE_KINDS


class TestClass(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    repo = models.ForeignKey('repository.Repository', related_name='testclasses')

    class Meta:
        verbose_name = 'Test Class'
        verbose_name_plural = 'Test Classes'

    def __unicode__(self):
        return self.name


class TestMethod(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    testclass = models.ForeignKey(TestClass, related_name='methods')

    class Meta:
        verbose_name = 'Test Method'

    def __unicode__(self):
        return self.name


class TestSuiteRun(models.Model):
    suite_name = models.CharField(max_length=255, db_index=True)
    build_flow = models.ForeignKey('build.BuildFlow', related_name='test_suite_runs')
    kind = models.CharField(max_length=25, choices = TEST_SUITE_KINDS, default='Other')
    tests_total = models.IntegerField(null=True, blank=True)
    tests_pass = models.IntegerField(null=True, blank=True)
    tests_fail = models.IntegerField(null=True, blank=True)

class TestResultManager(models.Manager):
    def update_summary_fields(self):
        for summary in self.all():
            summary.update_summary_fields()

    def compare_results(self, build_flows):

        results = OrderedDict()
        for build_flow in build_flows:
            for result in build_flow.test_results.all():
                cls = result.method.testclass.name
                method = result.method.name

                if not cls in results:
                    results[cls] = OrderedDict()

                if not method in results[cls]:
                    results[cls][method] = {}

                for limit in result.get_limit_types():
                    test_limit = 'test_{}_used'.format(limit)

                    if test_limit not in results[cls][method]:
                        results[cls][method][test_limit] = OrderedDict()

                    results[cls][method][test_limit][build_flow.id] = getattr(result, test_limit)

        diff = OrderedDict()

        for cls, methods in results.items():
            for method, limits in methods.items():
                for limit, build_flows in limits.items():
                    # Are any values different between the build_flows?
                    if len(set(build_flows.values())) > 1:
                        if not cls in diff:
                            diff[cls] = OrderedDict()

                        if not method in diff[cls]:
                            diff[cls][method] = {}

                        if limit not in diff[cls][method]:
                            diff[cls][method][limit] = OrderedDict()

                        diff[cls][method][limit] = build_flows

        return diff


class TestResult(models.Model):
    build_flow = models.ForeignKey('build.BuildFlow', related_name='test_results')
    test_suite_run = models.ForeignKey(TestSuiteRun, related_name='test_results', null=True)
    method = models.ForeignKey(TestMethod, related_name='test_results')
    duration = models.FloatField(null=True, blank=True, db_index=True)
    outcome = models.CharField(max_length=16, choices=OUTCOME_CHOICES, db_index=True)
    stacktrace = models.TextField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    source_file = models.CharField(max_length=255)
    
    # Apex Limits Statistics 
    test_email_invocations_used = models.IntegerField(null=True, blank=True, db_index=True)
    test_email_invocations_allowed = models.IntegerField(null=True, blank=True, db_index=True)
    test_email_invocations_percent = models.IntegerField(null=True, blank=True, db_index=True)
    test_soql_queries_used = models.IntegerField(null=True, blank=True, db_index=True)
    test_soql_queries_allowed = models.IntegerField(null=True, blank=True, db_index=True)
    test_soql_queries_percent = models.IntegerField(null=True, blank=True, db_index=True)
    test_future_calls_used = models.IntegerField(null=True, blank=True, db_index=True)
    test_future_calls_allowed = models.IntegerField(null=True, blank=True, db_index=True)
    test_future_calls_percent = models.IntegerField(null=True, blank=True, db_index=True)
    test_dml_rows_used = models.IntegerField(null=True, blank=True, db_index=True)
    test_dml_rows_allowed = models.IntegerField(null=True, blank=True, db_index=True)
    test_dml_rows_percent = models.IntegerField(null=True, blank=True, db_index=True)
    test_cpu_time_used = models.IntegerField(null=True, blank=True, db_index=True)
    test_cpu_time_allowed = models.IntegerField(null=True, blank=True, db_index=True)
    test_cpu_time_percent = models.IntegerField(null=True, blank=True, db_index=True)
    test_query_rows_used = models.IntegerField(null=True, blank=True, db_index=True)
    test_query_rows_allowed = models.IntegerField(null=True, blank=True, db_index=True)
    test_query_rows_percent = models.IntegerField(null=True, blank=True, db_index=True)
    test_dml_statements_used = models.IntegerField(null=True, blank=True, db_index=True)
    test_dml_statements_allowed = models.IntegerField(null=True, blank=True, db_index=True)
    test_dml_statements_percent = models.IntegerField(null=True, blank=True, db_index=True)
    test_mobile_apex_push_used = models.IntegerField(null=True, blank=True, db_index=True)
    test_mobile_apex_push_allowed = models.IntegerField(null=True, blank=True, db_index=True)
    test_mobile_apex_push_percent = models.IntegerField(null=True, blank=True, db_index=True)
    test_heap_size_used = models.IntegerField(null=True, blank=True, db_index=True)
    test_heap_size_allowed = models.IntegerField(null=True, blank=True, db_index=True)
    test_heap_size_percent = models.IntegerField(null=True, blank=True, db_index=True)
    test_sosl_queries_used = models.IntegerField(null=True, blank=True, db_index=True)
    test_sosl_queries_allowed = models.IntegerField(null=True, blank=True, db_index=True)
    test_sosl_queries_percent = models.IntegerField(null=True, blank=True, db_index=True)
    test_queueable_jobs_used = models.IntegerField(null=True, blank=True, db_index=True)
    test_queueable_jobs_allowed = models.IntegerField(null=True, blank=True, db_index=True)
    test_queueable_jobs_percent = models.IntegerField(null=True, blank=True, db_index=True)
    test_callouts_used = models.IntegerField(null=True, blank=True, db_index=True)
    test_callouts_allowed = models.IntegerField(null=True, blank=True, db_index=True)
    test_callouts_percent = models.IntegerField(null=True, blank=True, db_index=True)
    worst_limit = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    worst_limit_percent = models.IntegerField(null=True, blank=True, db_index=True)
    worst_limit_test = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    worst_limit_test_percent = models.IntegerField(null=True, blank=True, db_index=True)

    objects = TestResultManager()

    class Meta:
        verbose_name = 'Test Result'
        verbose_name_plural = 'Test Results'

    def __unicode__(self):
        return '%s.%s' % (self.method.testclass, self.method.name)
