from django.contrib import admin
from.models import Client,Domain,TenantData,TenantInfo



class DomainAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        if request.user.email != 'hkobir1973@gmail.com':
            return {}
        return super().get_model_perms(request)



class ClientAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        if request.user.email != 'hkobir1973@gmail.com':
            return {}
        return super().get_model_perms(request)


class TenantDataAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        if request.user.email != 'hkobir1973@gmail.com':
            return {}
        return super().get_model_perms(request)


admin.site.register(Domain, DomainAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(TenantData,TenantDataAdmin)

admin.site.register(TenantInfo)

