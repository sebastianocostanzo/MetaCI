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
    list_display = ('name', 'repo')
admin.site.register(TestClass, TestClassAdmin)

class TestSuiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'repo')

    def get_formset(self, request, obj=None, **kwargs):
            # Hack! Hook parent obj just in time to use in formfield_for_manytomany
        self.rrr = obj
        return super(TestSuiteAdmin, self).get_formset(request, obj, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "test_classes":
            kwargs["queryset"] = TestClass.objects.filter(repo = self.rrr.repo)
        return super(TestSuiteAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

admin.site.register(TestSuite, TestSuiteAdmin)