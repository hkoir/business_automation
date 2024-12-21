
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.utils import timezone
from datetime import datetime,timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q,F,Avg,Sum
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import uuid,json


from utils import create_notification,calculate_task_score,distribute_team_score,calculate_total_performance

from .models import PerformanceEvaluation, Employee,QualitativeEvaluation,Task,TeamMember,Team
from .forms import QualitativeEvaluationForm,TaskForm
from .forms import TeamForm,AddMemberForm
from .forms import TaskProgressForm,TaskAssignmentForm,RequestExtensionForm,ApproveExtensionForm

from core.forms import CommonFilterForm
from datetime import date
from django.db.models import Sum, F, ExpressionWrapper, FloatField
import openpyxl
from django.http import HttpResponse

from core.models import Position
from collections import defaultdict
from.forms import MonthlyQuarterlyTrendForm,YearlyTrendForm


def tasks_dashboard(request):
    return render(request, 'tasks/task_dashboard.html')




def create_team(request):
    teams = Team.objects.all().order_by('-created_at')   
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        teams = teams.filter(created_at__range=[start_date, end_date])
    else:            
        seven_days_ago = timezone.now() - timedelta(days=7)
        teams = teams.filter(created_at__gte=seven_days_ago)  
    
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team= form.save(commit=False)
            team.save()
            messages.success(request, 'Team created successfully!')
            create_notification(request.user,f"A team named '{team.name}' has been created with manager: {team.manager} for {team.description}")
            return redirect('tasks:create_team')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
   
    paginator = Paginator(teams, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = TeamForm()
    return render(request, 'tasks/create_team.html', {'form': form,'page_obj':page_obj,'teams':teams})


def delete_team(request, team_id):  
    team = get_object_or_404(Team, id=team_id)
    if request.method == 'POST':
        team.delete()
        messages.success(request, "Team has been successfully deleted.")
        create_notification(request.user,f'team-{team.name} has been deleted by {request.user} on {timezone.now()}')
        return redirect('tasks:create_team') 
    return render(request, 'tasks/delete_record.html', {'team': team})



def add_member(request):
    members = TeamMember.objects.all().order_by('-created_at')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        members = members.filter(created_at__range=[start_date, end_date])
    else:
        seven_days_ago = timezone.now() - timedelta(days=7)
        members = members.filter(created_at__gte=seven_days_ago)

    if request.method == 'POST':
        form = AddMemberForm(request.POST)
        if form.is_valid():
            form_data = form.save(commit=False)
            form_data.save()
 
            member = form_data.member if hasattr(form_data, 'member') else None
            team = form_data.team if hasattr(form_data, 'team') else None

            if member and team:
                create_notification(
                    request.user,
                    f'Member {member.name} has been added to the team {team.name}'
                )
                messages.success(request, 'Member added to the team successfully!')
            else:
                messages.warning(request, 'Member added, but notification creation failed due to missing data.')

            return redirect('tasks:add_member')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    else:
        pass
    paginator = Paginator(members, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = AddMemberForm()
    return render(request, 'tasks/add_member.html', {'form': form,'members':members,'page_obj':page_obj})



def add_member_with_id(request,team_id):
    team = get_object_or_404(Team, id=team_id)
    members = TeamMember.objects.all().order_by('-created_at')

    if request.method == 'POST':
        form = AddMemberForm(request.POST)
        if form.is_valid():
            form_data = form.save(commit=False)
            form_data.save()
            messages.success(request, 'Member added to the team successfully!')
            create_notification(request.user,f'member {team.members.first.member.name} has been added to the team {team.name}')
            return redirect('tasks:create_team')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    else:
        form = AddMemberForm()
    return render(request, 'tasks/add_member.html', {'form': form,'members':members,'team':team})


def delete_member(request, team_id):  
    team = get_object_or_404(TeamMember, id=team_id)
    if request.method == 'POST':
        team.delete()
        messages.success(request, "member has been successfully deleted.")
        create_notification(request.user,f'member {team.member.name} has been deleted frrom team {team.team.name}, deleted by {request.user} dated {timezone.now()}')
        return redirect('tasks:add_member') 
    return render(request, 'tasks/delete_record.html', {'team': team})




@login_required
def create_task(request):
    tasks = Task.objects.all().order_by('-created_at')   

    if not request.user.groups.filter(name='managers').exists():
        messages.success(request, 'You are not authorized to create task')
        return redirect('tasks:tasks_dashboard')


    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
         tasks =  tasks.filter(created_at__range=[start_date, end_date])
    else:            
        seven_days_ago = timezone.now() - timedelta(days=7)
        tasks = tasks.filter(created_at__gte=seven_days_ago)  

    if request.method == 'POST':
        form = TaskForm(request.POST)
        
        if form.is_valid():
            task = form.save(commit=False)
            assigned_to = form.cleaned_data['assigned_to']
            
            if assigned_to == 'team':
                task.assigned_to_team = form.cleaned_data['assigned_to_team']
                task.assigned_to_employee = None  
            elif assigned_to == 'member':
                task.assigned_to_employee = form.cleaned_data['assigned_to_employee']
                task.assigned_to_team = None  
            
            task.save()
            messages.success(request, 'Task created successfully!')
            create_notification(request.user,f'Task:{task.title}, has been created and assigned to  {task.assigned_to_team}-{task.assigned_to_employee}, manager::{task.task_manager} created by {request.user} dated {timezone.now()}')
            return redirect('tasks:create_task')
       
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    
    paginator = Paginator(tasks, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = TaskForm()    
    return render(request, 'tasks/create_tasks.html', {'form': form, 'tasks': tasks,'page_obj':page_obj})




def delete_task(request, task_id):  
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.delete()
        messages.success(request, f"{task} has been successfully deleted.")
        return redirect('tasks:add_member') 
    return render(request, 'tasks/delete_record.html', {'task': task})



def tasks_list(request):
    form = CommonFilterForm(request.GET)
    tasks = Task.objects.all().order_by('-created_at')  
    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        department = form.cleaned_data['department']

        if start_date and end_date:
           tasks = tasks.filter(created_at__range=(start_date, end_date))  
        else:            
            seven_days_ago = timezone.now() - timedelta(days=7)
            tasks = tasks.filter(created_at__gte=seven_days_ago)   
        if department:
            tasks = tasks.filter(department=department)

    
    paginator = Paginator(tasks, 8)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = CommonFilterForm()
    return render(request,'tasks/tasks_list.html',{'tasks':tasks,'page_obj':page_obj,'form':form})




def update_task_progress(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskProgressForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
           
            new_obtained_number = task.calculate_obtained_number()
            task.obtained_number = new_obtained_number
            task.obtained_score = (new_obtained_number / task.assigned_number) * 100 if task.assigned_number else 0

            if task.progress >= 100:
                task.status = 'COMPLETED'
            elif task.progress > 0:
                task.status = 'IN_PROGRESS'
            else:
                task.status = 'PENDING'

            task.save()

            # Update PerformanceEvaluation
            if task.assigned_to_team:
                team_members = TeamMember.objects.filter(team=task.assigned_to_team)
                for member in team_members:
                    evaluation, created = PerformanceEvaluation.objects.get_or_create(
                        employee=member.member,
                        task=task,
                        team=task.assigned_to_team,
                        defaults={
                            'quantitative_score': 0,
                            'remarks': 'Progressive evaluation in progress.',
                        }
                    )                    
                                    
                    evaluation.quantitative_score = (task.obtained_number / task.assigned_number) * 100 if task.assigned_number else 0
                    evaluation.obtained_quantitative_number = task.obtained_number
                    evaluation.assigned_quantitative_number = task.assigned_number

                    evaluation.remarks = f"Progress: {task.progress}%. Updated incremental score."
                    create_notification(request.user,f'Task:{task.title}, progress  {task.progress}% updated by {request.user} dated {timezone.now()}')
                    evaluation.save()

            elif task.assigned_to_employee:
                evaluation, created = PerformanceEvaluation.objects.get_or_create(
                    employee=task.assigned_to_employee,
                    task=task,
                    defaults={
                        'quantitative_score': 0,
                        'remarks': 'Progressive evaluation in progress.',
                    }
                )
                evaluation.quantitative_score = task.obtained_score
                evaluation.obtained_quantitative_number= task.obtained_number
                evaluation.assigned_quantitative_number = task.assigned_number
               
                evaluation.remarks = f"Progress: {task.progress}%. Updated incremental score."
                evaluation.save()

            messages.success(request, "Task progress updated successfully.")
            create_notification(request.user,f'Task:{task.title}, progress {task.progress}% updated by {request.user} dated {timezone.now()}')
            return redirect('tasks:tasks_list')
        else:
            messages.error(request, "Error updating task progress.")
    else:
        form = TaskProgressForm(instance=task)
    return render(request, 'tasks/update_progress.html', {'form': form, 'task': task})



def request_extension(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if task.assigned_to_employee:
        if task.assigned_to_employee.id == request.user.id:
            pass
        else:
            messages.info(request, "You are not allowed to update this task.")
            return redirect('tasks:tasks_list')    

    if task.assigned_to_team:
        team_members = task.assigned_to_team.members.all()  
        if any(member.member.id == request.user.id and member.is_team_leader for member in team_members):  
            pass
        else:
            messages.info(request, "Only team leader. can request time estension.")
            return redirect('tasks:tasks_list')

    if request.method == 'POST' and task.status == 'IN_PROGRESS':
        form = RequestExtensionForm(request.POST)
        if form.is_valid():
            extension_date = form.cleaned_data['extension_date']
            extension_time = form.cleaned_data['extension_time']

            try:
                extension_datetime_str = f"{extension_date} {extension_time}"
                extension_request_datetime = timezone.datetime.strptime(extension_datetime_str, '%Y-%m-%d %H:%M')
                
                task.extension_request_datetime = extension_request_datetime
                task.extension_requested = True
                task.status = 'TIME_EXTENSION'
                task.save()
                create_notification(request.user, task)
                messages.success(request, 'Extension request submitted successfully.')
            except ValueError:
                messages.error(request, 'Invalid date or time format.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    else:
        form = RequestExtensionForm()
    return render(request, 'tasks/request_extension.html', {'form': form, 'task': task})



def approve_extension(request, task_id):
    task = get_object_or_404(Task, id=task_id) 

    if task.assigned_to_employee:
        if task.task_manager.id == request.user.id:
            pass
        else:
            messages.info(request, "You are not authorize to approve")
            return redirect('tasks:tasks_list')    

    if task.assigned_to_team:
        if task.assigned_to_team.manager.id == request.user.id or task.task_manager.id == request.user.id:        
            pass
        else:
            messages.info(request, "Only team manager or Task manager can approve time extension.")
            return redirect('tasks:tasks_list')
        
    if request.method == 'POST' and task.status == 'TIME_EXTENSION':
        form = ApproveExtensionForm(request.POST)
        if form.is_valid():
            approve = form.cleaned_data['approve'] == 'yes'
            task.extension_approval = approve

            if approve:
                approval_date = form.cleaned_data['approval_date']
                approval_time = form.cleaned_data['approval_time']

                approval_datetime_str = f"{approval_date} {approval_time}"
                approval_datetime = datetime.strptime(approval_datetime_str, '%Y-%m-%d %H:%M')

                task.extended_due_date = approval_datetime
                task.status = 'IN_PROGRESS'
            else:
                task.status = 'OVERDUE'            
            task.manager_comments = form.cleaned_data['comments']
            task.save()
            messages.success(request, 'Extension request has been approved.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    else:
        form = ApproveExtensionForm()
    return render(request, 'tasks/approve_extension.html', {'form': form, 'task': task})




def performance_evaluation_view(request):
    form = CommonFilterForm(request.GET)
    evaluations = PerformanceEvaluation.objects.none()  
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        employee = form.cleaned_data.get('employee')

        department = form.cleaned_data.get('department')
        position = form.cleaned_data.get('position')

        evaluations = PerformanceEvaluation.objects.all().order_by('-evaluation_date')

        if start_date and end_date:
            evaluations = evaluations.filter(created_at__range=(start_date, end_date))
        if employee:
            evaluations = evaluations.filter(employee__name__icontains=employee)
        if department:
            evaluations = evaluations.filter(department__name__icontains=department)
        if position:
            evaluations = evaluations.filter(position__name__icontains=position)
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"Error in {field}: {error}")

    paginator = Paginator(evaluations, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = CommonFilterForm()
    return render(request, 'tasks/performance_evaluation_view.html', {
        'evaluations': evaluations,
        'form': form,
        'page_obj':page_obj
    })



@login_required
def create_qualitative_evaluation(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if task.task_manager.user_profile.user == request.user:
        pass
    else:
        messages.info(request, "This is a performance evaluation process of task. Only Task manager can evaluate performance.")
        return redirect('tasks:tasks_list')

    def calculate_performance_quality_score(evaluations):      
        
        total_score = 0
        total_items = 0
        max_score_per_item = 5.0 
        total_max_score = max_score_per_item * 5 

        for evaluation in evaluations:
            total_score += (
                evaluation.work_quality_score +
                evaluation.communication_quality_score +
                evaluation.teamwork_score +
                evaluation.initiative_score +
                evaluation.punctuality_score
            )
            total_items += 5 
        
        if total_items > 0:
            average_score = total_score / total_items
            percentage_score = (average_score / max_score_per_item) * 100        

            return total_max_score, total_score, percentage_score
        return 0, 0, 0
    
        
    if request.method == 'POST':
        form = QualitativeEvaluationForm(request.POST)
        if form.is_valid():
            qualitative_evaluation = form.save(commit=False)
            qualitative_evaluation.evaluator = request.user
            if qualitative_evaluation.manager_given_quantitative_number >task.assigned_number:
                messages.info(request, f'Quantitative score can not be more than assigned score-{task.assigned_score}')
                return redirect('tasks:tasks_list')
            
            if task.assigned_to_team:
                team_members = TeamMember.objects.filter(team=task.assigned_to_team)
                if team_members.exists():
                    total_team_members = team_members.count()
                    manager_given_number = qualitative_evaluation.manager_given_quantitative_number
                    manager_given_score =(manager_given_number / task.assigned_number) * 100  
                 

                    for member in team_members:                       
                        performance_evaluation, _ = PerformanceEvaluation.objects.get_or_create(
                            task=task,
                            employee=member.member,
                            team=task.assigned_to_team,
                            defaults={'quantitative_score': 0.0, 'qualitative_score': 0.0},
                        )                        
                        
                        QualitativeEvaluation.objects.create(
                            performance_evaluation=performance_evaluation,
                            employee=member.member,
                            task=task,
                            team = task.assigned_to_team,
                            evaluator=request.user,
                            manager_given_quantitative_number=qualitative_evaluation.manager_given_quantitative_number,
                            manager_given_quantitative_score=manager_given_score,
                           
                            work_quality_score=qualitative_evaluation.work_quality_score,
                            communication_quality_score=qualitative_evaluation.communication_quality_score,
                            teamwork_score=qualitative_evaluation.teamwork_score,
                            initiative_score=qualitative_evaluation.initiative_score,
                            punctuality_score=qualitative_evaluation.punctuality_score,
                            feedback=qualitative_evaluation.feedback,
                        )                        
                       
                        evaluations = QualitativeEvaluation.objects.filter(performance_evaluation=performance_evaluation)
                                              
                        total_max_score, total_score, percentage_score = calculate_performance_quality_score(evaluations)                                       
                                              
                        performance_evaluation.obtained_qualitative_number = total_score
                        performance_evaluation.assigned_qualitative_number = total_max_score
                        performance_evaluation.qualitative_score = percentage_score 

                        performance_evaluation.manager_given_quantitative_number = manager_given_number    
                        performance_evaluation.manager_given_quantitative_score = manager_given_score
                      
                        performance_evaluation.save()

                    task.original_obtained_score = task.obtained_score
                    task.obtained_score = manager_given_score
                    task.save()
                        
                    messages.success(request, f"Qualitative evaluation for the team '{task.assigned_to_team.name}' was successfully saved.")
                    create_notification(request.user,f'Task:{task.title}, manager evaluation completed by Mr {request.user} dated {timezone.now()}')
                else:
                    messages.error(request, "No members found in the assigned team.")
            
            elif task.assigned_to_employee:               
                performance_evaluation, _ = PerformanceEvaluation.objects.get_or_create(
                    task=task,
                    employee=task.assigned_to_employee,
                    defaults={'quantitative_score': 0.0, 'qualitative_score': 0.0},
                )                

                qualitative_evaluation.employee = task.assigned_to_employee
                qualitative_evaluation.performance_evaluation = performance_evaluation
                qualitative_evaluation.save()                
               
                evaluations = QualitativeEvaluation.objects.filter(performance_evaluation=performance_evaluation)
                total_max_score, total_score, percentage_score = calculate_performance_quality_score(evaluations)                                       
                                              
                performance_evaluation.obtained_qualitative_number = total_score
                performance_evaluation.assigned_qualitative_number = total_max_score
                performance_evaluation.qualitative_score = percentage_score 

                manager_given_number = qualitative_evaluation.manager_given_quantitative_number
                manager_given_score =(manager_given_number / task.assigned_number) * 100  
                            
                performance_evaluation.manager_given_quantitative_number = manager_given_number
                performance_evaluation.manager_given_quantitative_score = manager_given_score               

                performance_evaluation.save()

                task.original_obtained_score = task.obtained_score
                task.original_obtained_number = task.obtained_number

                task.obtained_score =  manager_given_score 
                task.obtained_number =  manager_given_number
               
                task.save()   
                create_notification(request.user,f'Task:{task.title}, manager evaluation completed by Mr {request.user} dated {timezone.now()}')             
                messages.success(request, f"Qualitative evaluation for {task.assigned_to_employee.name} was successfully saved.")
            else:
                messages.error(request, "No employee or team assigned to this task.")            
            return redirect('tasks:tasks_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    else:
        form = QualitativeEvaluationForm(initial={'task': task})
    return render(request, 'tasks/qualitative_evaluation_form.html', {'form': form, 'task': task})



def aggregated_report_sheet(request):
    evaluations = PerformanceEvaluation.objects.all()
    aggregated_report = []
    form = CommonFilterForm(request.GET)

    if form.is_valid():
        year = form.cleaned_data.get('year')
        employee = form.cleaned_data.get('employee')
        department = form.cleaned_data.get('department')
        position = form.cleaned_data.get('position')

        if year:
            evaluations = evaluations.filter(year=year)

        if employee:
            evaluations = evaluations.filter(employee__name__icontains=employee)

        if department:
            evaluations = evaluations.filter(department__name=department)

        if position:
            evaluations = evaluations.filter(position__name=position)

        aggregated_report = evaluations.values(
            'employee__id', 'employee__name', 'year', 'department__name', 'position__name'
        ).annotate(
            avg_quantitative_score=ExpressionWrapper(
                Sum('obtained_quantitative_number') / Sum('assigned_quantitative_number') * 100,
                output_field=FloatField()
            ),
            avg_manager_given_quantitative_score=ExpressionWrapper(
                Sum('manager_given_quantitative_number') / Sum('assigned_quantitative_number') * 100,
                output_field=FloatField()
            ),
            avg_qualitative_score=ExpressionWrapper(
                Sum('obtained_qualitative_number') / Sum('assigned_qualitative_number') * 100,
                output_field=FloatField()
            ),
            total_assigned_quantitative_number=Sum('assigned_quantitative_number'),
            total_assigned_qualitative_number=Sum('assigned_qualitative_number'),
            total_assigned_number=ExpressionWrapper(
                Sum('assigned_quantitative_number') + Sum('assigned_qualitative_number'),
                output_field=FloatField()
            ),
            total_obtained_number=ExpressionWrapper(
                Sum('obtained_quantitative_number') + Sum('obtained_qualitative_number'),
                output_field=FloatField()
            ),
            total_given_number=ExpressionWrapper(
                Sum('manager_given_quantitative_number') + Sum('obtained_qualitative_number'),
                output_field=FloatField()
            ),
            over_all_obtained_score=ExpressionWrapper(
                (Sum('obtained_quantitative_number') + Sum('obtained_qualitative_number')) /
                (Sum('assigned_quantitative_number') + Sum('assigned_qualitative_number')) * 100,
                output_field=FloatField()
            ),
            over_all_given_score=ExpressionWrapper(
                (Sum('manager_given_quantitative_number') + Sum('obtained_qualitative_number')) /
                (Sum('assigned_quantitative_number') + Sum('assigned_qualitative_number')) * 100,
                output_field=FloatField()
            ),
        )

    if request.GET.get('export') == 'true':
        return export_to_excel(aggregated_report)

    return render(request, 'tasks/aggregated_report_sheet.html', {
        'aggregated_report': aggregated_report,
        'form': form,
    })


def export_to_excel(aggregated_report):
    if not aggregated_report:
        return HttpResponse("No data available for export.", content_type="text/plain")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Aggregated Report"
    headers = [
        "Employee", "Year", "Avg Quantitative Score (%)", "Avg Manager Given Quantitative Score (%)",
        "Avg Qualitative Score (%)", "Total Assigned Quantitative Number", "Total Assigned Qualitative Number",
        "Total Assigned Number", "Total Obtained Number", "Total Given Number",
        "Overall Obtained Score (%)", "Overall Given Score (%)"
    ]
    ws.append(headers)

    # Populate rows
    for report in aggregated_report:
        row = [
            report.get('employee__name'),
            report.get('year'),
            report.get('avg_quantitative_score', 0),
            report.get('avg_manager_given_quantitative_score', 0),
            report.get('avg_qualitative_score', 0),
            report.get('total_assigned_quantitative_number', 0),
            report.get('total_assigned_qualitative_number', 0),
            report.get('total_assigned_number', 0),
            report.get('total_obtained_number', 0),
            report.get('total_given_number', 0),
            report.get('over_all_obtained_score', 0),
            report.get('over_all_given_score', 0),
        ]
        ws.append(row)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=aggregated_report.xlsx'
    wb.save(response)
    return response



def export_to_excel(aggregated_report):    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Aggregated Report"
    
    headers = [
        "Employee", "Year", "Avg quantitative Score(%)", "Avg manager given quantitative score(%)",
        "Avg qualitative score(%)", "Total assigned quantitative number", "Total assigned qualitative number", 
        "Total Assigned Number", "Total obtained number", "Total given number", "Overall obtained score(%)", "Overall given score(%)"
    ]
    ws.append(headers)

    for report in aggregated_report:
        total_obtained = report.get('total_obtained_number', 0)
        total_assigned = report.get('total_assigned_number', 0)
        total_given = report.get('total_given_number', 0)

        if total_assigned > 0:
            over_all_obtained_score = (total_obtained / total_assigned) * 100
        else:
            over_all_obtained_score = 0

        if total_assigned > 0:
            over_all_given_score = (total_given / total_assigned) * 100
        else:
            over_all_given_score = 0

        row = [
            report.get('employee__name'),
            report.get('year'),
            report.get('avg_quantitative_score', 0),
            report.get('avg_manager_given_quantitative_score', 0),
            report.get('avg_qualitative_score', 0),
            report.get('total_assigned_quantitative_number', 0),
            report.get('total_assigned_qualitative_number', 0),
            report.get('total_assigned_number', 0),
            total_obtained, 
            total_given,  
            over_all_obtained_score,  
            over_all_given_score, 
        ]

        ws.append(row)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=aggregated_report.xlsx'
    wb.save(response)
    return response


  
def employee_performance_chart(request):  
    tasks = Task.objects.filter(assigned_to='employee')  
    employee_scores = []
    employee=None
    department=None
    has_data=False

    form = CommonFilterForm(request.GET)

    if form.is_valid():
        employee = form.cleaned_data.get('employee_name') 
        department = form.cleaned_data.get('department') 
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        evaluations_by_date =PerformanceEvaluation.objects.none()

        if start_date and end_date:
            evaluations_by_date=PerformanceEvaluation.objects.filter(evaluation_date__range=(start_date,end_date)).distinct()       

        if department:
            evaluations_by_date = evaluations_by_date.filter(department__name__icontains=department)
       
        if employee:
            evaluations_by_date = evaluations_by_date.filter(employee__name__icontains=employee)            
        
             
        evaluations_by_date = evaluations_by_date.values('evaluation_date').annotate(
        assigned_quantitative_number=Sum('assigned_quantitative_number'),
        assigned_qulaitative_number=Sum('assigned_qualitative_number'),

        obtained_qualitative_number=Sum('obtained_qualitative_number'),
        manager_given_quantitative_number=Sum('manager_given_quantitative_number'),
        )

        for eval_date in evaluations_by_date:
            assigned_quantitative_number2 = eval_date['assigned_quantitative_number']  # * QUANTITATIVE_WEIGHT
            assigned_qulaitative_number2 = eval_date['assigned_qulaitative_number']  # * QUALITATIVE_WEIGHT
            obtained_qualitative_number2 = eval_date['obtained_qualitative_number']  # * QUANTITATIVE_WEIGHT
            manager_given_quantitative_number2 = eval_date['manager_given_quantitative_number']
            total_score = ((obtained_qualitative_number2+ manager_given_quantitative_number2) / (assigned_quantitative_number2 + assigned_qulaitative_number2)) * 100
            total_score = min(total_score, 100)  # Cap the score at 100
            
            employee_scores.append({
                'created_at': eval_date['evaluation_date'].strftime('%Y-%m-%d'),
                'total_score': total_score,
                'employee_name': employee.name if employee else 'unknown'
            })
            has_data=bool(employee_scores)

    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"Error in {field}: {error}")

    chart_data = json.dumps( employee_scores)

    paginator = Paginator(employee_scores, 6)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 


    form = CommonFilterForm() 
    return render(request, 'tasks/employee_performance_chart.html', {
        'chart_data': chart_data,
        'employee_scores': employee_scores,
        'form': form,
        'page_obj':page_obj,
        'employee':employee,
        'department':department,
        'has_data':has_data
    })





def team_performance_chart(request):  
    tasks = Task.objects.filter(assigned_to='team')  
    team_scores_over_time = []
    has_data=False

    form = CommonFilterForm(request.GET)
    if form.is_valid():
        team_name = form.cleaned_data.get('team_name', '').strip()
        department = form.cleaned_data.get('department')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        teams = Team.objects.none()
        if start_date and end_date:            
            teams=Team.objects.filter(team_ev__evaluation_date__range=(start_date,end_date)).distinct()
        if team_name:
            teams = teams.filter(name__icontains=team_name)
        if department:
            teams = teams.filter(department__name=department)
        
        # teams = Team.objects.all() if not team_name else Team.objects.filter(name__icontains=team_name)

        for team in teams:
            for task in tasks.filter(assigned_to_team=team):
                evaluations_by_date = PerformanceEvaluation.objects.filter(
                    team=team, task=task                        
                ).values('created_at__date').annotate(
                    assigned_quantitative_number=Sum('assigned_quantitative_number'),
                    assigned_qulaitative_number=Sum('assigned_qualitative_number'),
                    obtained_qualitative_number=Sum('obtained_qualitative_number'),
                    manager_given_quantitative_number=Sum('manager_given_quantitative_number'),
                )

                for eval_date in evaluations_by_date:
                    assigned_quantitative_number2 = eval_date['assigned_quantitative_number']
                    assigned_qulaitative_number2 = eval_date['assigned_qulaitative_number']
                    obtained_qualitative_number2 = eval_date['obtained_qualitative_number']
                    manager_given_quantitative_number2 = eval_date['manager_given_quantitative_number']
                    total_score = ((obtained_qualitative_number2 + manager_given_quantitative_number2) /
                                   (assigned_quantitative_number2 + assigned_qulaitative_number2)) * 100
                    total_score = min(total_score, 100)

                    team_scores_over_time.append({
                        'team': team.name,
                        'created_at': eval_date['created_at__date'].strftime('%Y-%m-%d'),
                        'score': total_score
                    })
                    has_data = bool(team_scores_over_time)

    else:
        print(f"Form errors: {form.errors}")

    paginator = Paginator(team_scores_over_time, 6)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)   

    form = CommonFilterForm() 
    return render(request, 'tasks/team_performance_chart.html', {
        'chart_data': json.dumps(team_scores_over_time),
        'team_scores': team_scores_over_time,
        'form': form,
        'page_obj':page_obj,
        'team_name':team_name,
        'department':department,
        'has_data':has_data
    })



def year_month_performance_chart(request):
    year = None
    employee_name = None
    form = CommonFilterForm(request.GET)
    report_data = []
    has_data=None
    department=None

    if form.is_valid():
        department = form.cleaned_data['department']
        employee_name = form.cleaned_data['employee_name']
        year = form.cleaned_data.get('year')

        employee = None
        if employee_name and department:
            employee = Employee.objects.filter(
                name__icontains=employee_name,
                department__name__icontains=department
            ).first()

        if employee_name:
            employee = Employee.objects.filter(
               name__icontains=employee_name               
            ).first()
       
        if employee:
            evaluations = PerformanceEvaluation.objects.filter(
                evaluation_date__year=year,
                employee=employee
            ).values('evaluation_date__month', 'evaluation_date__year').annotate(
                    assigned_quantitative_number=Sum('assigned_quantitative_number'),
                    assigned_qulaitative_number=Sum('assigned_qualitative_number'),
                    obtained_qualitative_number=Sum('obtained_qualitative_number'),
                    manager_given_quantitative_number=Sum('manager_given_quantitative_number'),
            )
            for eval_date in evaluations:
                assigned_quantitative_number2 = eval_date['assigned_quantitative_number']  # * QUANTITATIVE_WEIGHT
                assigned_qulaitative_number2 = eval_date['assigned_qulaitative_number']  # * QUALITATIVE_WEIGHT
                obtained_qualitative_number2 = eval_date['obtained_qualitative_number']  # * QUANTITATIVE_WEIGHT
                manager_given_quantitative_number2 = eval_date['manager_given_quantitative_number']
                total_score = ((obtained_qualitative_number2+ manager_given_quantitative_number2) / (assigned_quantitative_number2 + assigned_qulaitative_number2)) * 100
                total_score = min(total_score, 100)  # Cap the score at 100

            def get_month_name(month_number):
                month_names = [
                    'January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December'
                ]
                return month_names[month_number - 1]  

            for entry in evaluations:
                month_number = entry['evaluation_date__month']
                year_number = entry['evaluation_date__year']
                month_name = get_month_name(month_number)  

                report_data.append({
                    'created_at': month_name,  
                    'total_score': total_score,
                })

    chart_labels = [data['created_at'] for data in report_data]  
    total_scores = [data['total_score'] for data in report_data]
    has_data=bool(report_data)

    chart_data = {
        "labels": chart_labels,
        "total_scores": total_scores,
    }

    chart_data_json = json.dumps(chart_data)

  
    paginator = Paginator(report_data, 6)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)   

    form = CommonFilterForm()
    return render(request, 'tasks/year_month_performance_chart.html', {
        'form': form,
        'year': year,
        'employee_name': employee_name if employee_name else '',
        'report_data': report_data,
        'chart_data_json': chart_data_json,
        'page_obj':page_obj,
        'has_data':has_data,
        'department':department
    })




def year_quarter_performance_chart(request):
    year=None
    employee_name = None
    form = MonthlyQuarterlyTrendForm(request.GET)
    report_data = {}  
    has_data=None
    department=None

    if form.is_valid():
        department = form.cleaned_data.get('department')
        employee_name = form.cleaned_data['employee']
        year = form.cleaned_data.get('year')

        if department:
            employee = Employee.objects.filter(name__icontains=employee_name,department__name=department).first()
        else:
            employee = Employee.objects.filter(name__icontains=employee_name).first()

        evaluations = PerformanceEvaluation.objects.filter(
            evaluation_date__year=year,
            employee=employee
        ).values('quarter').annotate(
            assigned_quantitative_number=Sum('assigned_quantitative_number'),
            assigned_qulaitative_number=Sum('assigned_qualitative_number'),
            obtained_qualitative_number=Sum('obtained_qualitative_number'),
            manager_given_quantitative_number=Sum('manager_given_quantitative_number'),
        )

        for eval_date in evaluations:
                assigned_quantitative_number2 = eval_date['assigned_quantitative_number']  # * QUANTITATIVE_WEIGHT
                assigned_qulaitative_number2 = eval_date['assigned_qulaitative_number']  # * QUALITATIVE_WEIGHT
                obtained_qualitative_number2 = eval_date['obtained_qualitative_number']  # * QUANTITATIVE_WEIGHT
                manager_given_quantitative_number2 = eval_date['manager_given_quantitative_number']
                total_score = ((obtained_qualitative_number2+ manager_given_quantitative_number2) / (assigned_quantitative_number2 + assigned_qulaitative_number2)) * 100
                total_score = min(total_score, 100)  # Cap the score at 100

        report_data = {}
        for entry in evaluations:
            quarter = entry['quarter']
            quarter_name = f"{quarter}"
            report_data[quarter_name] = {               
                'total_score': total_score,
            }
   

    chart_labels = list(report_data.keys())   
    total_scores = [data['total_score'] for data in report_data.values()]
    has_data = bool(report_data)

    chart_data = {
        "labels": chart_labels,       
        "total_scores": total_scores,
    }

    chart_data_json = json.dumps(chart_data)  

    report_data_items = list(report_data.items())  
    paginator = Paginator(report_data_items, 6)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)   

    form=MonthlyQuarterlyTrendForm()
    return render(request, 'tasks/year_quarter_performance_chart.html', {
        'form': form,
        'year': year,
        'employee_name': employee_name if 'employee_name' in locals() else '',
        'report_data': report_data,
        'chart_data_json': chart_data_json,  
        'page_obj':page_obj,
        'has_data':has_data,
        'department':department
    })




def yearly_performance_trend(request):
    employee_scores = {}
    chart_data = {}
    employee_name = None
    department = None
    has_data=None

    form = YearlyTrendForm(request.GET)

    if form.is_valid():
        employee_name = form.cleaned_data.get('employee_name')
        start_year = form.cleaned_data.get('start_year')
        end_year = form.cleaned_data.get('end_year')
        department = form.cleaned_data.get('department')

       
        if start_year and not end_year:
            end_year = start_year
        elif not start_year and end_year:
            start_year = end_year
        if not start_year and not end_year:
            start_year = 2000
            end_year = date.today().year

        employees = Employee.objects.all()
        if department:
            employees = employees.filter(department__name__icontains=department)

        employee = employees.filter(name__icontains=employee_name).first() if employee_name else None

        if employee:
            evaluations = PerformanceEvaluation.objects.filter(
                employee=employee,
                evaluation_date__year__gte=start_year,
                evaluation_date__year__lte=end_year,
            ).values(
                'evaluation_date__year'
            ).annotate(
                assigned_quantitative_number=Sum('assigned_quantitative_number'),
                assigned_qulaitative_number=Sum('assigned_qualitative_number'),
                obtained_qualitative_number=Sum('obtained_qualitative_number'),
                manager_given_quantitative_number=Sum('manager_given_quantitative_number'),
            ).order_by('evaluation_date__year')

            for evaluation in evaluations:
                year = evaluation['evaluation_date__year']               

                assigned_quantitative_number2 = evaluation.get('assigned_quantitative_number', 0) or 0
                assigned_qulaitative_number2 = evaluation.get('assigned_qulaitative_number', 0) or 0
                obtained_qualitative_number2 = evaluation.get('obtained_qualitative_number', 0) or 0
                manager_given_quantitative_number2 = evaluation.get('manager_given_quantitative_number', 0) or 0

                denominator = assigned_quantitative_number2 + assigned_qulaitative_number2
                if denominator > 0:
                    total_score = (
                        (obtained_qualitative_number2 + manager_given_quantitative_number2) / denominator
                    ) * 100
                    total_score = min(total_score, 100)
                    employee_scores[year] = {'total_score': round(total_score, 2)}
                    print(f"Year: {year}, Total Score: {total_score}")
                else:
                    print(f"Year: {year}, Skipped due to zero denominator")

            chart_data = json.dumps(employee_scores)
   
        has_data = bool(employee_scores)

    employee_scores_items = list(employee_scores.items())
    paginator = Paginator(employee_scores_items, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form = YearlyTrendForm()
    return render(request, 'tasks/yearly_performance_trend.html', {
        'form': form,
        'chart_data': chart_data,
        'employee_scores': employee_scores,
        'employee_name': employee_name,
        'department': department,
        'page_obj': page_obj,
        'has_data':has_data
    })




def group_performance_chart(request):
    employee_data = {}
    chart_data={}

    form = CommonFilterForm(request.GET)
    if form.is_valid():
        position = form.cleaned_data.get('position')
        department = form.cleaned_data.get('department')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        evaluations = PerformanceEvaluation.objects.none()

        if position:
            evaluations = PerformanceEvaluation.objects.filter(position__name=position)
        if department:
            evaluations = evaluations.filter(department__name=department)
        if start_date and end_date:
            evaluations = evaluations.filter(evaluation_date__range=(start_date, end_date))

        evaluations = (
            evaluations.values("employee__name", "evaluation_date")
            .annotate(average_score=Avg("total_score"))
            .order_by("evaluation_date")
        )

        for evaluation in evaluations:
            employee_name = evaluation["employee__name"]
            date = evaluation["evaluation_date"].strftime('%Y-%m-%d')
            average_score = round(evaluation["average_score"], 2)

            if employee_name not in employee_data:
                employee_data[employee_name] = {
                    "dates": [],
                    "scores": [],
                }

            employee_data[employee_name]["dates"].append(date)
            employee_data[employee_name]["scores"].append(average_score)

        all_dates = sorted({date for data in employee_data.values() for date in data["dates"]})

        colors = [
            "rgba(255, 99, 132, 1)",  # Red
            "rgba(54, 162, 235, 1)",  # Blue
            "rgba(255, 206, 86, 1)",  # Yellow
            "rgba(75, 192, 192, 1)",  # Teal
            "rgba(153, 102, 255, 1)",  # Purple
            "rgba(255, 159, 64, 1)",  # Orange
        ]
        
        if position:
            chart_data = {
                "labels": all_dates,
                "datasets": [
                    {
                        "label": f'{employee_name}-{position}',
                        "data": [
                            employee_data[employee_name]["scores"][employee_data[employee_name]["dates"].index(date)]
                            if date in employee_data[employee_name]["dates"]
                            else None
                            for date in all_dates
                        ],
                        "borderColor": colors[i % len(colors)],
                        "backgroundColor": colors[i % len(colors)].replace("1)", "0.6)"),
                        "borderWidth": 2,
                        "fill": False,
                        "tension": 0.4,
                    }
                    for i, employee_name in enumerate(employee_data.keys())
                ],
            }

        else:
            chart_data = {}
        has_data = bool(chart_data.get("datasets"))



    flattened_data = []
    for employee_name, data in employee_data.items():
        for date, score in zip(data["dates"], data["scores"]):
            flattened_data.append({
                "employee": employee_name,
                "date": date,
                "score": score,
            })

    paginator = Paginator(flattened_data, 8)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form = CommonFilterForm()
    context = {
        "chart_data": json.dumps(chart_data),
        "evaluations": evaluations,
        "form": form,
        "page_obj": page_obj,
        'has_data':has_data
    }
    return render(request, "tasks/group_performance_chart.html", context)
