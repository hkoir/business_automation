from django.contrib import admin

from.models import Task,TeamMember, Team,PerformanceEvaluation,QualitativeEvaluation

admin.site.register(Task)
admin.site.register(Team)
admin.site.register(TeamMember)
admin.site.register(PerformanceEvaluation)
admin.site.register(QualitativeEvaluation)

