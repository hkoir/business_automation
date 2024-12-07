from django.contrib import admin
from.models import Client,Domain,TenantApplication,TenantInfo



admin.site.register(Client)
admin.site.register(Domain)
admin.site.register(TenantApplication)
admin.site.register(TenantInfo)






