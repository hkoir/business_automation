
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
import requests
from django.conf import settings
from django.http import JsonResponse
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import now
from django.db import transaction, connection
from django.core.mail import send_mail
from django.db import IntegrityError

from django_tenants.utils import get_public_schema_name
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from .models import TenantInfo,Tenant,Client,Domain,SubscriptionPlan, PaymentProfile,Subscription
from .forms import TenantApplicationForm,CreditCardPaymentForm




def tenant_dashboard(request):  
    plans = SubscriptionPlan.objects.all().order_by('duration')
    for plan in plans:
        plan.features_list = plan.features.split(',') if plan.features else [] 

    tenant_links = [
        {'name': 'only_core_dashboard', 'url': reverse('core:only_core_dashboard')},
        {'name': 'home', 'url': reverse('core:home')},
        {'name': 'tasks_dashboard', 'url': reverse('tasks:tasks_dashboard')},
        {'name':'transport:management_summary_report','url':reverse('transport:management_summary_report')}
    ]
   
    tenant = get_object_or_404(Client, schema_name=request.tenant.schema_name)
    tenant = getattr(request, 'tenant', None)
  
    is_public_schema = tenant.schema_name == get_public_schema_name()
    tenant_schema_name = request.tenant.schema_name
         

    if is_public_schema:
        template_name = "tenant/default_dashboard.html"
        context = {
            "welcome_message": "Welcome to the public dashboard",
            'plans':plans

        }
    else:
        template_name = "tenant/tenant_dashboard.html"
        context = {
            "tenant": tenant,
            "welcome_message": f"Welcome to {tenant.name}'s Dashboard!",
            'tenant_links':tenant_links,
            'plans':plans
        }
    return render(request, template_name, context)


def tenant_expire_check(request):
    tenant = getattr(request, 'tenant', None)
    if tenant:
        tenant_instance = tenant.tenant.first()
        if tenant_instance and tenant_instance.subscription and tenant_instance.subscription.expiration_date:
            if tenant_instance.subscription.expiration_date < timezone.now().date():
                return redirect('clients:renew_tenant')

    if not request.user.is_authenticated:
        return redirect('clients:dashboard')

    if request.user.is_authenticated:
        user_profile = getattr(request.user, 'user_profile', None)
        if not user_profile:
            return redirect('clients:create_user_profile')
        if request.user.groups.filter(name='Customer').exists():
            return redirect('customerportal:ticket_list')
        elif request.user.groups.filter(name='job_seekers').exists():
            return redirect('customerportal:job_list_candidate_view')
        else:
            return redirect('core:dashboard')
    else:
        return redirect('core:dashboard')

       


def create_user_profile(request):
    user_instance = request.user
    user_profile = UserProfile.objects.filter(user=user_instance).first()
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('clients:dashboard')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'tenant/user_profile.html', {'form': form})



PaymentGatewayAPI=None

def process_payment(payment_token, amount, currency='usd'):
    payment_gateway = PaymentGatewayAPI(api_key="your_api_key")    
    try:
        charge_response = payment_gateway.charge_card(
            token=payment_token,
            amount=amount,
            currency=currency
        )
        
        if charge_response['status'] == 'success':
            return True
        else:
            return False
    except Exception as e:
        return False


def check_payment_info(request, plan_id):
    if not PaymentProfile.objects.filter(user=request.user).exists():
        return redirect('clients:save_payment_info', plan_id=plan_id)
    return None



def apply_for_tenant_subscription(request):  
    plan_id = request.GET.get('plan_id')
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    payment_check = check_payment_info(request, plan_id)
    if payment_check:
        return payment_check

    payment_profile = PaymentProfile.objects.get(user=request.user)
    payment_token = payment_profile.payment_token 
    
    amount = plan.pric
    currency = 'usd' 
    
    if not process_payment(payment_token, amount, currency):
        messages.error(request, "Payment processing failed. Please try again.")
        return redirect('clients:save_payment_info', plan_id=plan_id)
    
    if request.method == 'POST':
        form = TenantApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            subdomain = form.cleaned_data['subdomain']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['name']  
            logo = form.cleaned_data['logo']  

            try:
                with transaction.atomic():  
                  
                    if Client.objects.filter(schema_name=subdomain).exists():
                        messages.error(request, "A tenant with this subdomain already exists.")
                        return render(request, 'tenant/apply_for_tenant.html', {'form': form, 'plan': plan})
                    
                    if User.objects.filter(username=name).exists():
                        messages.error(request, "A user with this username already exists.")
                        return render(request, 'tenant/apply_for_tenant.html', {'form': form, 'plan': plan})

                    tenant = Client.objects.create(schema_name=subdomain, name=subdomain)
                    tenant.save()
                    
                    domain = Domain(domain=f"{subdomain}.localhost", tenant=tenant, is_primary=True)
                    domain.save()                    
      
                    if not request.user.is_authenticated:
                        user = User.objects.create_user(
                            username=form.cleaned_data['email'],
                            email=form.cleaned_data['email'],
                            password=password 
                        )
                        user.is_superuser = True
                        user.is_staff = True  
                        user.save()                  

                    tenant_instance = Tenant.objects.create(
                        user=user,
                        tenant=tenant,
                        name=name,
                        subdomain=subdomain,
                        email=email,
                        phone_number=form.cleaned_data['phone_number'],
                        address=form.cleaned_data['address'],
                        logo=logo,
                    )

                    Subscription.objects.create(
                        tenant=tenant_instance,
                        subscription_plan=plan,
                        expiration_date=now().date() + timedelta(days=plan.duration * 30),
                        is_renewal=False,
                        status='active',
                    )
                
                    send_tenant_email(email, name, password, subdomain)

                    messages.success(request, 'Tenant created successfully. Credentials sent to your email.')
                    return redirect('accounts:login')
            except IntegrityError as e:
                messages.error(request, f"Error: {e}")
    else:
        form = TenantApplicationForm()    
    return render(request, 'tenant/apply_for_tenant.html', {'form': form, 'plan': plan})




def save_payment_info(request,plan_id):  
    plan_id = request.GET.get('plan_id')
    if request.method == 'POST':
        form = CreditCardPaymentForm(request.POST)
        if form.is_valid():
            card_number = form.cleaned_data['card_number']
            expiry_date = form.cleaned_data['expiry_date']
            cvv = form.cleaned_data['cvv']

            payment_gateway = PaymentGatewayAPI(api_key="your_api_key")
            try:        
                payment_token = payment_gateway.save_card(
                    card_number=form.cleaned_data['card_number'],
                    expiry_date=form.cleaned_data['expiry_date'],
                    cvv=form.cleaned_data['cvv'],
                    user_id=request.user.id
                )
                card_last4 = card_number[-4:]
                card_brand = "Visa"
                expiry_month, expiry_year = map(int, expiry_date.split('/'))

                PaymentProfile.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'payment_token': payment_token,
                        'card_last4': card_last4,
                        'card_brand': card_brand,
                        'card_expiry_month': expiry_month,
                        'card_expiry_year': expiry_year,
                    }
                )

                messages.success(request, "Payment information saved successfully!")
                return redirect(reverse('clients:process_subscription') + f"?plan_id={plan_id}")
            except Exception as e:
                messages.error(request, f"Error saving payment information: {str(e)}")
        else:
            messages.error(request, "Invalid payment information. Please try again.")
    else:
        form = CreditCardPaymentForm()    
    return render(request, 'tenant/save_payment_info.html', {'form': form, 'plan_id': plan_id})



def send_tenant_email(email, username, password, subdomain):
    subject = "Your Tenant Credentials"
    message = (
        f"Welcome to our platform!\n\n"
        f"Your tenant has been created successfully.\n\n"
        f"Username: {username}\n"
        f"Password: {password}\n"
        f"Subdomain: {subdomain}\n"
        f"Login URL: http://{subdomain}.localhost\n\n"
        f"Thank you for using our service!"
    )
    send_mail(subject, message, 'your-email@example.com', [email])



def handle_renewal_success(user, plan):     
    subscription = user.subscription 
    subscription.subscription_plan = plan
    subscription.expiration_date += timedelta(days=plan.duration * 30) 
    subscription.save()

def renew_subscription(request):
    subscription =None
    current_date = timezone.now().date()
    plan_id = request.GET.get('plan_id')
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    user = request.user

    if not user.is_authenticated:
        messages.error(request, "Please login to renew your subscription")
        return redirect('clients:dashboard')
  
    user_profile = getattr(user, 'user_profile', None)
    if user_profile and user_profile.tenant:
        client = user_profile.tenant  
        tenant = Tenant.objects.filter(tenant=client).first() 
    else:
        messages.error(request, "No tenant found for this user.")
        return redirect('clients:dashboard')

    if not tenant:
        messages.error(request, "No tenant found for this client.")
        return redirect('clients:dashboard')

    plan_id = request.GET.get('plan_id')
    if not plan_id:
        messages.error(request, "No plan selected. Please select a valid plan.")
        return redirect('clients:dashboard')
  
    try:
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    except SubscriptionPlan.DoesNotExist:
        messages.error(request, "The selected subscription plan does not exist.")
        return redirect('clients:dashboard')

    try:
        subscription = tenant.subscription
    except Subscription.DoesNotExist:
        messages.error(request, "No subscription found for this tenant.")
        return redirect('clients:apply_for_tenant')
   
    if subscription.expiration_date < timezone.now().date():
        messages.error(request, "Your subscription has expired and cannot be renewed yet.")
        return redirect('clients:apply_for_tenant')
        
    current_plan = subscription.subscription_plan   

    try:
        payment_profile = PaymentProfile.objects.get(user=user)
        payment_token = payment_profile.payment_token
        has_saved_payment = True
    except PaymentProfile.DoesNotExist:
        has_saved_payment = False

    if not has_saved_payment:
        if request.method == 'POST':
            form =  CreditCardPaymentForm(request.POST)
            if form.is_valid():
                card_number = form.cleaned_data['card_number']
                expiry_date = form.cleaned_data['expiry_date']
                cvv = form.cleaned_data['cvv']
 
                payment_gateway = PaymentGatewayAPI(api_key="your_api_key")
                try:
                    charge_response = payment_gateway.charge_card(
                        card_number=card_number,
                        expiry_date=expiry_date,
                        cvv=cvv,
                        amount=int(plan.price * 100), 
                        currency='usd'
                    )

                    if charge_response['status'] == 'success':
                        handle_renewal_success(user, plan)
                        messages.success(request, "Your subscription has been successfully renewed!")
                        return redirect('clients:dashboard')
                    else:
                        messages.error(request, "Payment failed. Please try again.")
                except Exception as e:
                    messages.error(request, f"Payment error: {str(e)}")
        else:
            form = CreditCardPaymentForm()
        return render(request, 'tenant/renew_subscription.html', 
            {
            'form': form, 
            'subscription': subscription, 
            'plan': plan,
            ' current_date': current_date,
            'current_plan':current_plan
            })

    payment_gateway = PaymentGatewayAPI(api_key="your_api_key")
    try:
        charge_response = payment_gateway.charge_card(
            token=payment_token,
            amount=int(plan.price * 100), 
            currency='usd'
        )

        if charge_response['status'] == 'success':
            handle_renewal_success(user, plan)
            messages.success(request, "Your subscription has been successfully renewed!")
            return redirect('clients:dashboard')
        else:
            messages.error(request, "Payment failed. Please try again.")
    except Exception as e:
        messages.error(request, f"Payment error: {str(e)}")

    return redirect('clients:renew_subscription')




class Command(BaseCommand):
    help = 'Suspends tenants whose subscription has expired'

    def handle(self, *args, **kwargs):
        current_date = timezone.now().date()

        expired_tenants = Tenant.objects.filter(
            expiration_date__lt=current_date, 
            status='active'
        )

        # Suspend expired tenants
        for tenant in expired_tenants:
            tenant.status = 'suspended'
            tenant.save()
            self.stdout.write(self.style.SUCCESS(f"Suspended tenant: {tenant.name}"))



def thanks_for_application(request):
    rules = TenantInfo.objects.filter(name="Rules and Regulations").first()
    guidelines = TenantInfo.objects.filter(name="Branding Guidelines").first()

    return render(request, 'tenant/thanks_for_application.html', {
        'rules': rules,
        'guidelines': guidelines,
    })


