
from django.shortcuts import render, get_object_or_404,redirect,reverse
from django.contrib import messages

from clients.models import SubscriptionPlan


def common_view(request):
    plans = SubscriptionPlan.objects.all().order_by('duration')
    for plan in plans:
        plan.features_list = plan.features.split(',') 

    tenant_links = [
        {'name': 'only_core_dashboard', 'url': reverse('core:only_core_dashboard')},
        {'name': 'home', 'url': reverse('core:home')},
        {'name': 'tasks_dashboard', 'url': reverse('tasks:tasks_dashboard')},
    ]
    return render(request, 'commonapp/home.html', {'tenant_links': tenant_links,'plans': plans})

