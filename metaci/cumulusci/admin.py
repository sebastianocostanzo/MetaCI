from django.contrib import admin
from metaci.cumulusci.models import Org
from metaci.cumulusci.models import ScratchOrgInstance
from metaci.cumulusci.models import Service


class OrgAdmin(admin.ModelAdmin):
    list_display = ('name', 'repo', 'supertype', 'org_type', 'sf_org_id')
    list_filter = ('repo', 'supertype', 'org_type')

    fieldsets = (
        (
            None, {'fields':('name', 'repo', 'supertype', 'org_type', 'sf_org_id')}
        ),
        (
            'Description', {'fields':('description',)}
        ),
        (
            'DX/CCI Config', {'fields': ('json',)}
        ),
        (
            'Registered Org Config', {'fields':('push_schedule', 'owner')}
        )
    )
admin.site.register(Org, OrgAdmin)


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(Service, ServiceAdmin)


class ScratchOrgInstanceAdmin(admin.ModelAdmin):
    list_display = ('org', 'build', 'sf_org_id', 'username', 'deleted', 'time_created', 'time_deleted')
    list_filter = ('deleted', 'org')
admin.site.register(ScratchOrgInstance, ScratchOrgInstanceAdmin)
