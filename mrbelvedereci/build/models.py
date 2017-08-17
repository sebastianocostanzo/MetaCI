from __future__ import unicode_literals

import StringIO
from glob import iglob
import json
import os
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

from cumulusci.core.config import FlowConfig
from cumulusci.core.exceptions import ApexTestException
from cumulusci.core.exceptions import BrowserTestFailure
from cumulusci.core.exceptions import FlowNotFoundError
from cumulusci.core.utils import import_class
from cumulusci.salesforce_api.exceptions import MetadataComponentFailure
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
import requests

from mrbelvedereci.build.utils import format_log
from mrbelvedereci.build.utils import set_build_info
from mrbelvedereci.cumulusci.config import MrbelvedereGlobalConfig
from mrbelvedereci.cumulusci.config import MrbelvedereProjectConfig
from mrbelvedereci.cumulusci.keychain import MrbelvedereProjectKeychain
from mrbelvedereci.cumulusci.logger import init_logger
from mrbelvedereci.testresults.importer import import_test_results

BUILD_STATUSES = (
    ('queued', 'Queued'),
    ('waiting', 'Waiting'),
    ('running', 'Running'),
    ('success', 'Success'),
    ('error', 'Error'),
    ('fail', 'Failed'),
)
BUILD_FLOW_STATUSES = (
    ('queued', 'Queued'),
    ('running', 'Running'),
    ('success', 'Success'),
    ('error', 'Error'),
    ('fail', 'Failed'),
)
BUILD_TYPES = (
    ('manual', 'Manual'),
    ('auto', 'Auto'),
    ('scheduled', 'Scheduled'),
    ('legacy', 'Legacy - Probably Automatic')
)


class Build(models.Model):
    repo = models.ForeignKey('repository.Repository', related_name='builds')
    branch = models.ForeignKey('repository.Branch', related_name='builds',
                               null=True, blank=True)
    commit = models.CharField(max_length=64)
    commit_message = models.TextField(null=True, blank=True)
    tag = models.CharField(max_length=255, null=True, blank=True)
    pr = models.IntegerField(null=True, blank=True)
    plan = models.ForeignKey('plan.Plan', related_name='builds')
    org = models.ForeignKey('cumulusci.Org', related_name='builds', null=True,
                            blank=True)
    org_instance = models.ForeignKey('cumulusci.ScratchOrgInstance',
                                     related_name='builds', null=True, blank=True)
    schedule = models.ForeignKey('plan.PlanSchedule', related_name='builds',
                                 null=True, blank=True)
    log = models.TextField(null=True, blank=True)
    exception = models.TextField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=BUILD_STATUSES,
                              default='queued')
    keep_org = models.BooleanField(default=False)
    task_id_status_start = models.CharField(max_length=64, null=True,
                                            blank=True)
    task_id_check = models.CharField(max_length=64, null=True, blank=True)
    task_id_run = models.CharField(max_length=64, null=True, blank=True)
    task_id_status_end = models.CharField(max_length=64, null=True, blank=True)
    current_rebuild = models.ForeignKey('build.Rebuild',
                                        related_name='current_builds', null=True, blank=True)
    time_queue = models.DateTimeField(auto_now_add=True)
    time_start = models.DateTimeField(null=True, blank=True)
    time_end = models.DateTimeField(null=True, blank=True)

    build_type = models.CharField(max_length=16, choices=BUILD_TYPES, default='legacy')
    user = models.ForeignKey('users.User', related_name='builds', null=True, on_delete=models.PROTECT)

    class Meta:
        ordering = ['-time_queue']

    def __unicode__(self):
        return '{}: {} - {}'.format(self.id, self.repo, self.commit)

    def get_log_html(self):
        if self.log:
            return format_log(self.log)

    def get_absolute_url(self):
        return reverse('build_detail', kwargs={'build_id': str(self.id)})

    def get_external_url(self):
        url = '{}{}'.format(settings.SITE_URL, self.get_absolute_url())
        return url

    def get_build(self):
        return self.current_rebuild if self.current_rebuild else self

    def get_build_attr(self, attr):
        # get an attribute from the most recent build/rebuild
        build = self.get_build()
        return getattr(build, attr)

    def get_status(self):
        return self.get_build_attr('status')

    def get_exception(self):
        return self.get_build_attr('exception')

    def get_error_message(self):
        return self.get_build_attr('error_message')

    def get_time_queue(self):
        return self.get_build_attr('time_queue')

    def get_time_start(self):
        return self.get_build_attr('time_start')

    def get_time_end(self):
        return self.get_build_attr('time_end')

    def set_status(self, status):
        build = self.get_build()
        build.status = status
        build.save()

    def flush_log(self):
        for handler in self.logger.handlers:
            handler.stream.flush(force=True)

    def run(self):
        self.logger = init_logger(self)
        self.logger.info('-- Building commit {}'.format(self.commit))
        self.flush_log()
        build = self.current_rebuild if self.current_rebuild else self
        set_build_info(build, status='running', time_start=timezone.now())

        if self.schedule:
            self.logger.info('Build triggered by {} schedule #{}'.format(
                self.schedule.schedule, self.schedule.id))

        try:
            # Extract the repo to a temp build dir
            self.build_dir = self.checkout()

            # Change directory to the build_dir
            os.chdir(self.build_dir)

            # Initialize the project config
            project_config = self.get_project_config()

            # Set the sentry context for build errors
            sentry_environment = 'mrbelvedereci'
            project_config.config['sentry_environment'] = sentry_environment

            # Look up the org
            org_config = self.get_org(project_config)

        except Exception as e:
            self.logger.error(unicode(e))
            set_build_info(build, status='error', time_end=timezone.now())
            self.delete_build_dir()
            self.flush_log()
            return

        # Run flows
        try:
            flows = [flow.strip() for flow in self.plan.flows.split(',')]
            for flow in flows:
                self.logger = init_logger(self)
                self.logger.info('Running flow: {}'.format(flow))
                self.save()

                build_flow = BuildFlow(
                    build=self,
                    rebuild=self.current_rebuild,
                    flow=flow,
                )
                build_flow.save()
                build_flow.run(project_config, org_config)

                if build_flow.status != 'success':
                    self.logger = init_logger(self)
                    self.logger.error(
                        'Build flow {} completed with status {}'.format(
                            flow, build_flow.status))
                    self.logger.error('    {}: {}'.format(build_flow.exception,
                                                          build_flow.error_message))
                    set_build_info(
                        build,
                        status=build_flow.status,
                        exception=build_flow.exception,
                        error_message=build_flow.error_message,
                        time_end=timezone.now(),
                    )
                    self.flush_log()
                    if org_config.created:
                        self.delete_org(org_config)
                    return
                else:
                    self.logger = init_logger(self)
                    self.logger.info(
                        'Build flow {} completed successfully'.format(
                            flow))
                    self.flush_log()
                    self.save()

        except Exception as e:
            set_build_info(build, status='error', time_end=timezone.now())
            if org_config.created:
                self.delete_org(org_config)
            self.logger = init_logger(self)
            self.logger.error(unicode(e))
            self.delete_build_dir()
            self.flush_log()
            return

        if org_config.created:
            self.delete_org(org_config)

        self.delete_build_dir()
        self.flush_log()
        set_build_info(build, status='success', time_end=timezone.now())

    def checkout(self):
        zip_url = '{}/archive/{}.zip'.format(
            self.repo.url,
            self.commit,
        )
        self.logger.info('-- Download commit from URL: {}'.format(zip_url))
        self.save()
        kwargs = {'auth': (settings.GITHUB_USERNAME, settings.GITHUB_PASSWORD)}
        resp = requests.get(zip_url, **kwargs)
        build_dir = tempfile.mkdtemp()
        self.logger.info('-- Extracting zip to temp dir {}'.format(build_dir))
        self.save()
        zip_content = StringIO.StringIO(resp.content)
        zip_file = zipfile.ZipFile(zip_content)
        zip_file.extractall(build_dir)
        build_dir += '/{}-{}'.format(self.repo.name, self.commit)
        self.logger.info('-- Commit extracted to build dir: {}'.format(
            build_dir))
        self.save()

        if self.plan.sfdx_config:
            self.logger.info(
                '-- Injecting custom sfdx-workspace.json from plan')
            filename = os.path.join(build_dir, 'sfdx-workspace.json')
            with open(filename, 'w') as f:
                f.write(self.plan.sfdx_config)

        return build_dir

    def get_project_config(self):
        global_config = MrbelvedereGlobalConfig()
        project_config = global_config.get_project_config(self)
        keychain = MrbelvedereProjectKeychain(project_config, None, self)
        project_config.set_keychain(keychain)
        return project_config

    def get_org(self, project_config):
        org_config = project_config.keychain.get_org(self.plan.org)
        self.org = org_config.org
        if self.current_rebuild:
            self.current_rebuild.org_instance = org_config.org_instance
            self.current_rebuild.save()
        else:
            self.org_instance = org_config.org_instance
        self.save()
        return org_config

    def get_org_instance(self):
        if self.current_rebuild and self.current_rebuild.org_instance:
            return self.current_rebuild.org_instance
        else:
            return self.org_instance

    def get_org_attr(self, attr):
        org_instance = self.get_org_instance()
        obj = getattr(org_instance, attr, '')
        return obj() if callable(obj) else obj

    def get_org_deleted(self):
        return self.get_org_attr('deleted')

    def get_org_sf_org_id(self):
        return self.get_org_attr('sf_org_id')

    def get_org_name(self):
        return self.get_org_attr('__unicode__')

    def get_org_time_deleted(self):
        return self.get_org_attr('time_deleted')

    def get_org_url(self):
        return self.get_org_attr('get_absolute_url')

    def get_org_username(self):
        return self.get_org_attr('username')

    def delete_org(self, org_config):
        self.logger = init_logger(self)
        if not org_config.scratch:
            return
        if self.keep_org:
            self.logger.info(
                'Skipping scratch org deletion since keep_org was requested')
            return
        try:
            org_instance = self.get_org_instance()
            org_instance.delete_org(org_config)
        except Exception as e:
            self.logger.error(e.message)
            self.save()

    def delete_build_dir(self):
        if hasattr(self, 'build_dir'):
            self.logger.info('Deleting build dir {}'.format(self.build_dir))
            shutil.rmtree(self.build_dir)
            self.save()


class BuildFlow(models.Model):
    build = models.ForeignKey('build.Build', related_name='flows')
    rebuild = models.ForeignKey('build.Rebuild', related_name='flows',
                                null=True, blank=True)
    status = models.CharField(max_length=16, choices=BUILD_FLOW_STATUSES,
                              default='queued')
    flow = models.CharField(max_length=255, null=True, blank=True)
    log = models.TextField(null=True, blank=True)
    exception = models.TextField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    time_queue = models.DateTimeField(auto_now_add=True)
    time_start = models.DateTimeField(null=True, blank=True)
    time_end = models.DateTimeField(null=True, blank=True)
    tests_total = models.IntegerField(null=True, blank=True)
    tests_pass = models.IntegerField(null=True, blank=True)
    tests_fail = models.IntegerField(null=True, blank=True)
    test_suites = models.ManyToManyField('testresults.TestSuite')

    def __unicode__(self):
        return '{}: {} - {} - {}'.format(self.build.id, self.build.repo,
                                         self.build.commit, self.flow)

    def get_absolute_url(self):
        return reverse('build_detail', kwargs={
            'build_id': str(self.build.id)}) + '#flow-{}'.format(self.flow)

    def get_log_html(self):
        if self.log:
            return format_log(self.log)

    def run(self, project_config, org_config):
        # Record the start
        set_build_info(self, status='running', time_start=timezone.now())

        # Set up logger
        self.logger = init_logger(self)

        try:
            # Run the flow
            result = self.run_flow(project_config, org_config)

            # Load test results
            self.load_test_results()

            # Record result
            exception = None
            status = 'success'

        except MetadataComponentFailure as e:
            exception = e
            status = 'fail'

        except ApexTestException as e:
            exception = e
            self.load_test_results()
            status = 'fail'

        except BrowserTestFailure as e:
            exception = e
            self.load_test_results()
            status = 'fail'

        except Exception as e:
            exception = e
            status = 'error'

        kwargs = {
            'status': status,
            'time_end': timezone.now(),
        }
        if exception:
            if status == 'error':
                self.logger.error(unicode(e))
            kwargs['error_message'] = unicode(e)
            kwargs['exception'] = e.__class__.__name__
        set_build_info(self, **kwargs)

    def run_flow(self, project_config, org_config):
        # Add the repo root to syspath to allow for custom tasks and flows in
        # the repo
        sys.path.append(project_config.repo_root)

        flow = getattr(project_config, 'flows__{}'.format(self.flow))
        if not flow:
            raise FlowNotFoundError('Flow not found: {}'.format(self.flow))
        flow_config = FlowConfig(flow)

        # Get the class to look up options
        class_path = flow_config.config.get('class_path',
                                            'cumulusci.core.flows.BaseFlow')
        flow_class = import_class(class_path)

        # Create the flow and handle initialization exceptions
        self.flow_instance = flow_class(project_config, flow_config,
                                        org_config)

        # Run the flow
        res = self.flow_instance()

        return res

    def record_result(self):
        self.status = 'success'
        self.time_end = timezone.now()
        self.save()

    def load_test_results(self):
        results = []
        if self.build.plan.junit_path:
            for filename in iglob(self.build.plan.junit_path):
                results.extend(self.load_junit(filename))
            if not results:
                self.logger.warning('No results found at JUnit path {}'.format(
                    self.build.plan.junit_path
                ))
        try:
            results_filename = 'test_results.json'
            with open(results_filename, 'r') as f:
                results.extend(json.load(f))
            for result in results:
                result['SourceFile'] = results_filename
        except IOError as e:
            try:
                results_filename = 'test_results.xml'
                results.extend(self.load_junit(results_filename))
            except IOError as e:
                pass
        if not results:
            return
        import_test_results(self, results)

        self.tests_total = self.test_results.count()
        self.tests_pass = self.test_results.filter(outcome='Pass').count()
        self.tests_fail = self.test_results.filter(
            outcome__in=['Fail', 'CompileFail']).count()
        self.save()

    def load_junit(self, filename):
        results = []
        tree = ET.parse(filename)
        testsuite = tree.getroot()
        for testcase in testsuite.iter('testcase'):
            result = {
                'ClassName': testcase.attrib['classname'],
                'Method': testcase.attrib['name'],
                'Outcome': 'Pass',
                'StackTrace': '',
                'Message': '',
                'Stats': {
                    'duration': testcase.get('time'),
                },
                'SourceFile': filename,
            }
            for element in testcase.iter():
                if element.tag not in ['failure', 'error']:
                    continue
                result['Outcome'] = 'Fail'
                result['StackTrace'] += element.text + '\n'
                message = element.attrib['type']
                if 'message' in element.attrib:
                    message += ': ' + element.attrib['message']
                result['Message'] += message + '\n'
            results.append(result)
        return results


class Rebuild(models.Model):
    build = models.ForeignKey('build.Build', related_name='rebuilds')
    user = models.ForeignKey('users.User', related_name='rebuilds')
    org_instance = models.ForeignKey('cumulusci.ScratchOrgInstance',
                                     related_name='rebuilds', null=True, blank=True)
    status = models.CharField(max_length=16, choices=BUILD_STATUSES,
                              default='queued')
    exception = models.TextField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    time_queue = models.DateTimeField(auto_now_add=True)
    time_start = models.DateTimeField(null=True, blank=True)
    time_end = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-id']

    def get_absolute_url(self):
        return reverse('build_rebuild_detail', kwargs={
            'build_id': str(self.build.id), 'rebuild_id': str(self.id)})
