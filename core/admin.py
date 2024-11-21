from django.contrib import admin

from .models import Company,Location,Employee,Notice

admin.site.register(Company)
admin.site.register(Location)
admin.site.register(Employee)
admin.site.register(Notice)


