from django.contrib import admin
from django_tenants.admin import TenantAdminMixin




from .models import Company,Location,Employee,Notice,EmployeeRecordChange,AttendanceModel,MonthlySalaryReport


admin.site.register(Company)
admin.site.register(Location)
admin.site.register(Employee)
admin.site.register(Notice)

admin.site.register(EmployeeRecordChange)
admin.site.register(AttendanceModel)
admin.site.register(MonthlySalaryReport)




