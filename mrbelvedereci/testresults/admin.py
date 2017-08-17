from django.contrib import admin
from mrbelvedereci.testresults.models import TestResult
from mrbelvedereci.testresults.models import TestMethod
from mrbelvedereci.testresults.models import TestClass
from mrbelvedereci.testresults.models import TestSuite

class TestResultAdmin(admin.ModelAdmin):
    list_display = ('build_flow', 'method', 'duration', 'outcome')
    list_filter = ('build_flow__build__repo', 'method', 'method__testclass')
admin.site.register(TestResult, TestResultAdmin)

class TestMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'testclass')
    list_filter = ('testclass__repo', 'testclass')
admin.site.register(TestMethod, TestMethodAdmin)

class TestClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'repo', 'kind')
    list_filter = ('repo', 'kind')
admin.site.register(TestClass, TestClassAdmin)

class TestSuiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'repo', 'kind')
    list_filter = ('repo', 'kind')

admin.site.register(TestSuite, TestSuiteAdmin)