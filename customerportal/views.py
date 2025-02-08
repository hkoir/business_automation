from django.shortcuts import render,redirect,get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from utils import create_notification
from django.utils import timezone
from datetime import datetime, timedelta
from collections import defaultdict

from tasks.forms import CustomerUpdateTicketForm,TicketForm
from core.forms import CommonFilterForm
from tasks.models import TeamMember,PerformanceEvaluation,TaskMessageReadStatus,Ticket,Task

from recruitment.models import Job,Candidate,TakeExam,Exam
from recruitment.forms import SearchApplicationForm,CandidateForm,TakeExamForm
from django.utils.timezone import localtime
from django.urls import reverse
from django.db.models import Q
from repairreturn.forms import RepairReturnCustomerFeedbackForm
from.forms import TicketCustomerFeedbackForm
from tasks.models import Ticket


def create_ticket(request):    
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            priority = form.cleaned_data['priority']            
            ticket= form.save(commit=False)
            ticket.created_by = request.user
            ticket.user=request.user
            ticket.save()
           

            task = Task.objects.create(
                ticket=ticket,  
                progress=0.0,
                user=request.user,
                task_type='TICKET',
                title='Ticket',
                priority = priority
            )

            messages.success(request, 'Ticket and task  created successfully!')

            create_notification(request.user,f"A ticket with task '{ticket.subject}' has been created",'TICKET-NOTIFICATION')
            return redirect('customerportal:ticket_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
   
    form = TicketForm()
    return render(request, 'customerportal/create_ticket.html', {'form': form})


from.forms import FilterForm

def ticket_list(request):   
    form = FilterForm(request.GET)
    tickets = Ticket.objects.all().order_by('-created_at') 
   
    unread_messages = defaultdict(list) 
    unread_statuses = TaskMessageReadStatus.objects.filter(user=request.user, read=False)
    for status in unread_statuses:
        unread_messages[status.task_message.task.id].append(status.task_message)
      
       
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Customer').exists():
            tickets = tickets.filter(user = request.user)
        else:
            tickets = tickets
    for ticket in tickets:
        print(ticket.id, ticket.progress_by_customer)

    if request.method == 'GET':
        form = FilterForm(request.GET)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            ticket_number = form.cleaned_data['ticket_number']
            
            if start_date and end_date:
                tickets =  tickets.filter(created_at__range=(start_date, end_date))  
            if ticket_number:           
                tickets =  tickets.filter(ticket_id = ticket_number)    
        else:
            print(form.errors)
            form = FilterForm()
   
    paginator = Paginator(tickets, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = FilterForm()
    return render(request, 'customerportal/tickets_list.html', {'form': form,'page_obj':page_obj,'unread_messages':unread_messages})


def update_ticket(request, ticket_id):    
    ticket = get_object_or_404(Ticket, id=ticket_id)
    sale_return =None

# when update ticket at the same time we will update repair return object and task object

# Fetch repair return variables to update repair return object##################
    try:           
        sale_order = ticket.sales           
        if not sale_order:
            messages.info(request,'there is an error of fetching related field')
            raise AttributeError("No Sale Order found for the task ticket.")

        sale_order_item = sale_order.sale_order.first()            
        if not sale_order_item :
            messages.info(request,'there is an error of fetching related field')
            raise AttributeError("No Sale Returns found for the Sale Order.") 
        sale_return = sale_order_item.sale_returns.first()              
                                
    except AttributeError as e:
        messages.info(request,'there is an error of fetching related field')
        print(f"Error: {str(e)}")  
   

    if request.method == 'POST':
        form = CustomerUpdateTicketForm(request.POST, instance=ticket)  
        if form.is_valid():     
            customer_feedback = form.cleaned_data['customer_feedback']
            form = form.save(commit=False) 

            if customer_feedback == 'PROGRESS-100%':
                messages.success(request, f'Ticket have completed, can not update anymore')
                        
# update ticket data and repair return data ####################
            if customer_feedback == 'PROGRESS-20%':
                form.progress_by_customer = 20.0 # update ticket object
                sale_return.progress_by_customer = 20.0 # update repair return object object
            elif form.customer_feedback == 'PROGRESS-30%':
                form.progress_by_customer = 30.0
                sale_return.progress_by_customer = 30.0
            elif form.customer_feedback == 'PROGRESS-40%':
                form.progress_by_customer = 40.0
                sale_return.progress_by_customer = 40.0            
            elif customer_feedback == 'PROGRESS-50%':
                form.progress_by_customer = 50.0
                sale_return.progress_by_customer = 50.0
            elif customer_feedback == 'PROGRESS-60%':
                form.progress_by_customer = 60.0
                sale_return.progress_by_customer = 60.0
            elif customer_feedback == 'PROGRESS-70%':
               form. progress_by_customer = 70.0
               sale_return.progress_by_customer = 70.0
            elif customer_feedback == 'PROGRESS-80%':
                form.progress_by_customer = 80.0
                sale_return.progress_by_customer = 80.0
            elif customer_feedback == 'PROGRESS-90%':
                sale_return.progress_by_customer = 90.0
                form.progress_by_customer = 90.0
            elif customer_feedback == 'PROGRESS-100%':
                form.progress_by_customer = 100.0
                sale_return.progress_by_customer = 100.0
            else:
                form.progress_by_customer = 0.0
                sale_return.progress_by_customer = 0.0

            form.user = request.user
            form.save()
            sale_return.save()
           
    #############Update task data and calculate performance at the same time#############
   
            ### Update task progress
            for task in ticket.task.all():  
                task.progress = ticket.progress_by_customer  
                task.save() # task data updated #####################################

                # Calculate performance data
                new_obtained_number = task.calculate_obtained_number()
                task.obtained_number = new_obtained_number
                if task.assigned_number > 0:
                    task.obtained_score = (new_obtained_number / task.assigned_number) * 100 
                if task.progress >= 100:
                    task.status = 'COMPLETED'
                elif task.progress > 0:
                    task.status = 'IN_PROGRESS'
                else:
                    task.status = 'PENDING'
                task.save()
                if task.assigned_to_team:
                    team_members = TeamMember.objects.filter(team=task.assigned_to_team)
                    for member in team_members:
                        evaluation, created = PerformanceEvaluation.objects.get_or_create(
                            employee=member.member,
                            task=task,
                            team=task.assigned_to_team,
                            defaults={
                                'assigned_quantitative_number': 0,
                                'remarks': 'Progressive evaluation in progress.',
                            }
                        )
                        evaluation.obtained_quantitative_score = (task.obtained_number / task.assigned_number) * 100 if task.assigned_number else 0
                        evaluation.obtained_quantitative_number = task.obtained_number
                        evaluation.assigned_quantitative_number = task.assigned_number
                        evaluation.remarks = f"Progress: {task.progress}%. Updated incremental score."
                        create_notification(request.user, message= f'Task:{task.title}, progress {task.progress}% updated by {request.user} dated {timezone.now()}',notification_type='TASK-NOTIFICATION')
                        evaluation.save()
                elif task.assigned_to_employee:
                    evaluation, created = PerformanceEvaluation.objects.get_or_create(
                        employee=task.assigned_to_employee,
                        task=task,
                        defaults={
                            'assigned_quantitative_number': 0,
                            'remarks': 'Progressive evaluation in progress.',
                        }
                    )
                    evaluation.obtained_quantitative_score = task.obtained_score
                    evaluation.obtained_quantitative_number = task.obtained_number
                    evaluation.assigned_quantitative_number = task.assigned_number
                    evaluation.remarks = f"Progress: {task.progress}%. Updated incremental score."
                    evaluation.save()                            
                
                messages.success(request, f'Ticket updated successfully with feedback: {ticket.customer_feedback} complete!')
                create_notification(request.user, f"A ticket with subject '{ticket.subject}' has been updated", 'TICKET-NOTIFICATION')
                return redirect('customerportal:ticket_list')
        
                          
        else:  
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")

    else:
        form = CustomerUpdateTicketForm(instance=ticket)
    return render(request, 'customerportal/update_ticket.html', {'form': form})




def ticket_customer_feedback(request,ticket_id):
    tickets = Ticket.objects.all().order_by('-created_at')
    ticket_instance =get_object_or_404(Ticket,id=ticket_id)     
      
    form = TicketCustomerFeedbackForm(request.POST,request.FILES,instance=ticket_instance)
    if request.method == 'POST':
        form = TicketCustomerFeedbackForm(request.POST,request.FILES,instance=ticket_instance)
        if form.is_valid():         
            is_work_completed = form.cleaned_data['is_work_completed']
            repair_ticket = form.save(commit=False)
            repair_ticket.save()

            messages.success(request,'Thanks for your feedback')
            return redirect('customerportal:return_request_list')
        else:
            messages.info(request,'form is invalid')

    paginator =Paginator(tickets ,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)  

    form = TicketCustomerFeedbackForm(
                initial={
                    'ticket':ticket_instance,  
                }
            )
    return render(request, 'customerportal/ticket_customer_feedback.html',
         {
             'page_obj': page_obj,
             'form':form,
            
             
        })


# repair return sold product
from django.contrib.auth.decorators import login_required
from sales.models import SaleOrder,SaleOrderItem
from repairreturn.forms import ReturnOrRefundForm
from repairreturn.models import ReturnOrRefund

@login_required
def sale_order_list(request):
    sale_order_number=None
    form = CommonFilterForm(request.GET or None)
    sale_orders = SaleOrder.objects.all().order_by('-created_at')

    if form.is_valid():
        sale_order_number = form.cleaned_data['sale_order_id']
        if sale_order_number:
            sale_orders = sale_orders.filter(order_id = sale_order_number)
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field.capitalize()}: {error}")

    paginator = Paginator(sale_orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form=CommonFilterForm()

    return render(request, 'customerportal/sale_order_list.html',
        {
            'sale_orders':sale_orders,
            'form':form,
            'sale_order_number':sale_order_number,
            'page_obj':page_obj,
            'sale_order_number':sale_order_number
        })

from django.db import transaction

@login_required
def create_return_request(request, sale_order_id):
    sale_order = get_object_or_404(SaleOrder, id=sale_order_id)
    sales = sale_order.sale_order.all()
    return_requests = ReturnOrRefund.objects.prefetch_related('faulty_products__faulty_replacement').all()

    if request.method == 'POST':
        form = ReturnOrRefundForm(request.POST, sale_order_id=sale_order_id)  

        sale_id = request.POST.get('sale')
        try:
            sale = get_object_or_404(SaleOrderItem, id=sale_id)
        except:
            messages.error(request, "Invalid sale item selected.")
            return redirect(request.path)
        
        if form.is_valid():
            return_refund = form.save(commit=False)
            return_refund.sale = sale
            return_refund.user=request.user
            return_refund.save()

            with transaction.atomic():
                ticket = Ticket.objects.create(
                    sales=sale_order,  
                    progress_by_customer=0.0,
                    progress_by_user=0.0,
                    user=request.user,
                    ticket_type='REPAIR-RETRUN',               
                
                )

                task = Task.objects.create(
                    ticket=ticket,  
                    progress=0.0,
                    user=request.user,
                    task_type='TICKET',
                    title='Repair Return',
                
                )

            create_notification(
                request.user,
               message= f"Customer {sale_order.customer} has placed a repair/return request for: {sale.product}",
                notification_type='RETURN-NOTIFICATION'
            )
            messages.success(request, "A Task of Return/Refund request submitted successfully!")
            return redirect('customerportal:return_request_list')
        else:
            messages.error(request, "There was an error with your submission. Please check the form.")
    else:
        form = ReturnOrRefundForm(sale_order_id=sale_order_id) 

    paginator = Paginator(return_requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'customerportal/user_create_return_request.html', {
        'form': form,
        'sale_order': sale_order,
        'sales': sales,
        'return_requests': return_requests,
        'page_obj': page_obj
    })



@login_required
def return_request_progress(request, sale_order_id):
    sale_order = get_object_or_404(SaleOrder, id=sale_order_id)
    sales = sale_order.sale_order.all()  
    return_requests = ReturnOrRefund.objects.prefetch_related('faulty_products__faulty_replacement').all().order_by('-created_at')
      
    paginator =Paginator(return_requests,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'customerportal/return_request_progress.html', {
        'sale_order': sale_order,
        'sales': sales,
        'return_requests':return_requests,
        'page_obj':page_obj
    })


@login_required
def customer_return_request_list(request):
    return_id=None
    returns = ReturnOrRefund.objects.all().order_by('-created_at')
    form = CommonFilterForm(request.GET or None)
    if form.is_valid():
        return_id = form.cleaned_data['sale_order_id']
        if return_id:
            returns = returns.filter(sale__sale_order__order_id = return_id)
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field.capitalize()}: {error}")

    paginator =Paginator(returns ,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form=CommonFilterForm()
    return render(request, 'customerportal/user_return_request_list.html',
         {
             'page_obj': page_obj,
             'form':form,
             'page_obj':page_obj,
             'return_id':return_id
        })





def repair_return_customer_feedback(request,return_id):
    returns = ReturnOrRefund.objects.all().order_by('-created_at')
    return_instance =get_object_or_404(ReturnOrRefund,id=return_id)     
               
    feedback_instance = return_instance.return_feedback.first()    
    form = RepairReturnCustomerFeedbackForm(request.POST,request.FILES,instance=feedback_instance)
    if request.method == 'POST':
        form = RepairReturnCustomerFeedbackForm(request.POST,request.FILES,instance=feedback_instance)
        if form.is_valid():         
            is_work_completed = form.cleaned_data['is_work_completed']
            repair_ticket = form.save(commit=False)
            repair_ticket.save()

            messages.success(request,'Thanks for your feedback')
            return redirect('customerportal:return_request_list')
        else:
            messages.info(request,'form is invalid')

    paginator =Paginator(returns ,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)  

    form = RepairReturnCustomerFeedbackForm(
                initial={
                    'repair_return': return_instance,  
                }
            )
    return render(request, 'customerportal/customer_feedback.html',
         {
             'page_obj': page_obj,
             'form':form,
            
             
        })


from recruitment.models import  Candidate

def job_list_candidate_view(request): 
    jobs = Job.objects.all().order_by('-created_at')
    candidates = Candidate.objects.all()
    candidate = Candidate.objects.filter(candidate=request.user).first()   
    exam_start_time = None
    exam_end_time = None
    current_time = timezone.now() 

    applied_jobs = None

    if candidate:
        applied_jobs = Candidate.objects.filter(candidate=candidate.id).values_list('applied_job_id', flat=True)

    for job in jobs:        
        if job.deadline < timezone.now().date():
            job.is_active = False
            job.save()
            
        exams = job.job_exam.all()
        for exam in exams:
            exam_start_time = localtime(exam.start_time).isoformat()
            exam_end_time = localtime(exam.end_time).isoformat()        
 
    form = SearchApplicationForm(request.GET or None)    
    if request.method == 'GET':
        form = SearchApplicationForm(request.GET or None) 
        if form.is_valid():           
            query = form.cleaned_data.get('query')
            if query:
                jobs = jobs.filter(
                    Q(title__icontains=query) |
                    Q(candidates__full_name__icontains=query) |
                    Q(candidates__email__icontains=query)
                )
            else:
                jobs =jobs
        else:
            print(form.errors)
            form = SearchApplicationForm() 
  

    form = SearchApplicationForm() 
    paginator = Paginator(jobs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render (request,'customerportal/recruitment/job_list_candidate_view.html',{
        'jobs':jobs,
        'page_obj':page_obj,
         'jobs': jobs,
        'candidates': candidates,
        'candidate': candidate,
        'applied_jobs': applied_jobs, 
        'form':form,

        'exam_start_time':  exam_start_time,
        'exam_end_time':  exam_end_time,
        'current_time': localtime(current_time).isoformat(),
      
        })

from core.models import Position

def position_details(request,id):
    position_instance = get_object_or_404(Position,id=id)
    return render(request,'customerportal/recruitment/position_details.html',{'position_instance':position_instance})



def job_application(request, id):
    job = get_object_or_404(Job, id=id)
    candidate = job.candidates.filter(candidate=request.user).first()  
    if request.method == "POST":
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid(): 
            candidate_instance = form.save(commit=False)
            candidate_instance.candidate = request.user  
            candidate_instance.applied_job = job       
            candidate_instance.save()                
            form.save_m2m()             

            candidate_instance.cv_screening_score = candidate_instance.calculate_cv_screening_score()
            candidate_instance.save(update_fields=['cv_screening_score'])           

            messages.success(request, "Your job application has been submitted successfully.")
            return redirect('customerportal:job_list_candidate_view')
        else:
            messages.error(request, "There was an error with your application.")
    else:
        form = CandidateForm()

    return render(request, 'customerportal/recruitment/job_application_form.html', {
        'job': job,
        'form': form,
    })





def pre_take_exam(request, exam_id, candidate_id):
    exam = get_object_or_404(Exam, id=exam_id)
    candidate = get_object_or_404(Candidate, id=candidate_id)
    current_time = timezone.now()
    
    # If the exam is starting now, redirect to the exam page
    if current_time <= exam.start_time:
        return redirect('customerportal:take_exam', exam_id=exam.id, candidate_id=candidate.id)
    
    return render(request, 'customerportal/recruitment/pre_take_exam.html', {
        'exam': exam,
        'candidate': candidate,
        'exam_start_time': localtime(exam.start_time).isoformat(),
        'exam_end_time': localtime(exam.end_time).isoformat(),
        'current_time': localtime(current_time).isoformat(),
    })



def take_exam(request, exam_id, candidate_id):
    exam = get_object_or_404(Exam, id=exam_id)
    candidate = get_object_or_404(Candidate, id=candidate_id)

    # if candidate.status != 'Shortlisted':
    #     messages.info(request, "You are not shortlisted for this exam.")
    #     return redirect('recruitment:job_list')  

    current_time = timezone.now()
    # if exam.is_expired():
    #     messages.warning(request, 'The exam time has expired. You can no longer take this exam.')
    #     return redirect('recruitment:job_list')
    # if exam.start_time > current_time:
    #     messages.info(request, 'The exam has not started yet. Please wait.')
    #     return redirect('recruitment:job_list')

    questions = exam.questions.all()

    if request.method == "POST":
        form = TakeExamForm(questions, request.POST)
        if form.is_valid():
            if exam.end_time <= current_time:
                messages.warning(request, 'The exam time has expired. You cannot submit the exam paper.')
                return redirect('customerportal:job_list_candidate_view')

            total_marks = 0
            for question in questions:
                selected_option = form.cleaned_data.get(f'question_{question.id}')
                is_correct = selected_option == question.correct_answer  
                question_marks = question.marks if is_correct else 0  
                total_marks += question_marks

                TakeExam.objects.create(
                    candidate=candidate,
                    exam=exam,
                    question=question,
                    selected_option=selected_option,
                    obtained_marks=question_marks
                )

            TakeExam.objects.filter(candidate=candidate, exam=exam).update(obtained_marks=total_marks)
            candidate.status = 'EXAM-PASS' if total_marks >= exam.pass_marks else 'EXAM-FAIL'
            candidate.exam_score = total_marks
            candidate.save()   
            return redirect(reverse('customer_portal:job_list', kwargs={'exam_id': exam.id, 'candidate_id': candidate.id}))
    else:
        form = TakeExamForm(questions)
    return render(request, 'customerportal/recruitment/take_exam.html', {
        'exam': exam,
        'candidate': candidate,
        'form': form,
        'exam_start_time': localtime(exam.start_time).isoformat(),
        'exam_end_time': localtime(exam.end_time).isoformat(),
        'current_time': localtime(current_time).isoformat(),
    })




def selected_candidate_job_status(request): 
    jobs = Job.objects.all().order_by('-created_at')
    candidates = Candidate.objects.filter(candidate=request.user)
    candidate = Candidate.objects.filter(candidate=request.user).first()
    exam_start_time = None
    exam_end_time = None
    current_time = timezone.now()   

    for job in jobs:        
        if job.deadline < timezone.now().date():
            job.is_active = False
            job.save()
            
        exams = job.job_exam.all()
        for exam in exams:
            exam_start_time = localtime(exam.start_time).isoformat()
            exam_end_time = localtime(exam.end_time).isoformat()

            if exam.is_expired():
                messages.warning(request, 'The exam time has expired.')
            elif exam.start_time > current_time:
                messages.info(request, 'The exam has not started yet')

 
    form = SearchApplicationForm(request.GET or None)    
    if request.method == 'GET':
        form = SearchApplicationForm(request.GET or None) 
        if form.is_valid():
            print('form valid')
            query = form.cleaned_data.get('query')
            if query:
                jobs = jobs.filter(
                    Q(title__icontains=query) |
                    Q(candidates__full_name__icontains=query) |
                    Q(candidates__email__icontains=query)
                )
            else:
                jobs = jobs 
        else:
            print(form.errors,'...............form error')
            form = SearchApplicationForm() 
    else:
        print('error in get/post')

    form = SearchApplicationForm() 
    paginator = Paginator(jobs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render (request,'customerportal/recruitment/selected_candidate_job_status.html',{
        'jobs':jobs,
        'page_obj':page_obj,
         'jobs': jobs,
        'candidates': candidates,
        'candidate': candidate,
        'form':form,

        'exam_start_time':  exam_start_time,
        'exam_end_time':  exam_end_time,
        'current_time': localtime(current_time).isoformat(),
      
        })



def candidate_confirmation(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)

    # if candidate.confirmation_deadline and candidate.confirmation_deadline < timezone.now().date():
    #     messages.info(request, 'Your timing of confirmation has expired')
    #     return redirect("recruitment:selected_candidate")

    if request.method == "POST":
        decision = request.POST.get("decision")
        joining_date = request.POST.get("joining_date")
        if decision == "accept":
            candidate.offer_status = "accepted"
            candidate.confirmation_status = "accepted"
            if joining_date: 
                candidate.expected_joining_date = joining_date    
            candidate.save()            
            messages.success(request, f"Congratulation Dear Mr.{candidate.full_name}.Please meet with our hiring manager at your conveinent time within office hour")
            return redirect(reverse("recruitment:congratulations", args=[candidate.id]))
        else:
            candidate.offer_status = "declined"
            candidate.confirmation_status = "declined"
            candidate.save()
            messages.warning(request, f"{candidate.full_name} has declined the offer.")

        
       
        return redirect("recruitment:selected_candidate")  
    return render(request, "customerportal/recruitment/candidate_confirmation.html", {"candidate": candidate})
  

def congratulations(request, candidate_id):
    #candidate = get_object_or_404(Candidate, id=candidate_id, confirmation_status="accepted")
    candidate = get_object_or_404(Candidate, id=candidate_id)

    guidelines = [
        "Meet the hiring manager on your joining date.",
        "Bring original copies of your documents (ID proof, academic certificates, etc.).",
        "Sign the employment contract upon arrival.",
        "Complete your HR formalities and onboarding process.",
    ]
    return render(request, "customerportal/congratulations.html", {"candidate": candidate, "guidelines": guidelines})


from recruitment.models import CommonDocument,CandidateDocument
from core.forms import AddEmployeeForm
from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from django.core.mail import EmailMessage,send_mail


def candidate_joining(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)  
    # if not candidate.manager_confirmation_of_joining:
    #     messages.warning(request, "Hiring Manager has not approved the onboarding yet.")
    #     return redirect("customerportal:job_list_candidate_view")

    # if candidate.joining_deadline and candidate.joining_deadline < timezone.now().date():
    #     messages.warning(request, 'Your timing of joining has expired')
    #     return redirect("customerportal:job_list_candidate_view")

    if request.method == "POST":
        form = AddEmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)          
            employee.save()

            subject = f"Welcome to {candidate.applied_job.company} - Your Employment Details"
            message = render_to_string("recruitment/onboard_welcome_template.html", {"employee": employee})
            email = EmailMessage(
                subject,
                message,
                "hr@yourcompany.com",  
                [employee.email],  
            )
           
            common_documents = CommonDocument.objects.all()
            for doc in common_documents:
                email.attach(doc.name, doc.file.read(), doc.file.content_type)

            candidate_documents = CandidateDocument.objects.filter(candidate=candidate)
            for doc in candidate_documents:
                email.attach(doc.name, doc.file.read(), doc.file.content_type)

            email.send(fail_silently=False)         
                                
            candidate.hiring_status = True
            candidate.onboard_status = "onboard"
            candidate.save()
     
            if candidate.candidate:
                user = candidate.candidate
                job_seekers = Group.objects.get(name="Job_seekers")
                staff_group, _ = Group.objects.get_or_create(name="Staff")

                user.groups.remove(job_seekers)
                user.groups.add(staff_group)

            messages.success(request, f"{candidate.full_name} has officially joined the company.")
            return redirect("accounts:login")
    else:
       form = AddEmployeeForm(initial={
            "name": candidate.full_name,
            "email": candidate.email,  
            "salary_structure": candidate.applied_job.salary_structure,          
            "department": candidate.applied_job.department,
            "position": candidate.applied_job.position,  
            "location": candidate.applied_job.location,
            "joining_date": candidate.expected_joining_date,
            "company": candidate.applied_job.company,
            "gender": candidate.gender,
            'user_profile':candidate.candidate.user_profile,
           
        })
    return render(request, "customerportal/recruitment/candidate_joining.html", {"form": form, "candidate": candidate})
   


def search_applications(request):
    form = SearchApplicationForm(request.GET or None)  
    candidates = Candidate.objects.all()  

    if form.is_valid(): 
        query = form.cleaned_data.get('query')
        if query:   
            candidates = candidates.filter(
                full_name__icontains=query
            ) | candidates.filter(email__icontains=query)

    return render(request, 'customerportal/recruitment/search_applications.html', {
        'form': form,
        'candidates': candidates,
    })

