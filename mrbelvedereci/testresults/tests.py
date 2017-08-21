from django.test import TestCase
from mrbelvedereci.repository.models import Repository
from mrbelvedereci.plan.models import Plan
from mrbelvedereci.build.models import Build, BuildFlow
from mrbelvedereci.testresults.models import TestClass, TestMethod, TestResult, TestSuiteRun
from mrbelvedereci.testresults.importer import import_test_results
# Create your tests here.


def result_dict_member(**kwargs):
    result = {
        'ClassName': kwargs.get('class_name', 'TestClass'),
        'Method': kwargs.get('method', 'test_method'),
        'Outcome': kwargs.get('outcome', 'Pass'),
        'StackTrace': kwargs.get('stacktrace','[1.1] None'),
        'Message': kwargs.get('message', 'This was a test'),
        'Stats': {
            'duration': kwargs.get('time', 100),
        },
        'SourceFile': kwargs.get('sourcefile','TestClass'),
        'TestSuiteName': kwargs.get('test_suite_name', 'tests')
    }
    return result

class TestImporter(TestCase):
    # we want to test the importer function, which turns 
    # test_results.json style dicts into TestResult model objects
    
    def setUp(self):
        # need a repo, a plan, a build, a build flow
        self.repo = Repository(name='CumulusCI-Test', owner='SalesforceFoundation', 
                            public=True, url='https://github.com/SalesforceFoundation/CumulusCI-Test')
        self.repo.save()
        self.plan = Plan(name='Sample', type='manual', repo=self.repo, flows='junit', junit_path='junit/*.xml')
        self.plan.save()
        self.build = Build(repo=self.repo, plan=self.plan, commit='1a11a', status='success')
        self.build.save()
        self.build_flow = BuildFlow(build=self.build, flow='junit', status='success')
        self.build_flow.save()
        self.old_test_class = TestClass(repo=self.repo, name='Apex_TEST')
        self.old_test_class.save()

    def test_that_your_testsetup_worked(self):
        self.assertIsNotNone(self.repo.pk)
        self.assertIsNotNone(self.plan.pk)
        self.assertEqual(self.plan.repo.pk, self.repo.pk)

    def test_importer_creates_class_and_method(self):
        # results dict of two classes, three methods
        results = [
            result_dict_member(method='methoda'), 
            result_dict_member(method='methodb'), 
            result_dict_member(class_name='AnotherTest')
        ]

        bf = import_test_results(self.build_flow, results)

        # verify two classes, three methods
        self.assertEqual(3, TestMethod.objects.count())

        self.assertEqual(1, TestClass.objects.filter(name='TestClass').count())
        self.assertEqual(1, TestClass.objects.filter(name='AnotherTest').count())

    def test_importer_creates_testresult(self):
        results = [
            result_dict_member(stacktrace='[importer_creates_testresult]')]

        bf = import_test_results(self.build_flow, results)

        self.assertEqual(1, TestResult.objects.filter(stacktrace='[importer_creates_testresult]').count())

    def test_importer_creates_suite(self):
        results = [
            result_dict_member(test_suite_name='importer', method='test_a'),
            result_dict_member(test_suite_name='importer', method='test_b')]

        bf = import_test_results(self.build_flow, results)

        self.assertEqual(1, TestSuiteRun.objects.filter(suite_name='importer').count())


    def test_importer_finds_existing_class(self):
        results = [
            result_dict_member(class_name='Apex_TEST', method='test_apex_TEST')]

        bf = import_test_results(self.build_flow, results)

        test_method = TestMethod.objects.filter(name='test_apex_TEST').all()[0]
        self.assertEqual(test_method.testclass.pk, self.old_test_class.pk)
