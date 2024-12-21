
from . import views
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import logged_out_view  
from clients.views import tenant_expire_check


from django.views.generic import TemplateView
from.forms import PwdResetConfirmForm,PwdResetForm



app_name = 'accounts'

urlpatterns = [
    path('', tenant_expire_check, name='tenant_expire_check'),
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:logged_out'), name='logout'),
 
   
   ###################################################################################################
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_reset/password_change.html',
            success_url='/password_change/done/'), name='password_change' ),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_reset/password_change_done.html', ),
          name='password_change_done'),
    ################################################################################

      # Reset password
    path("password_reset/", auth_views.PasswordResetView.as_view( template_name="accounts/password_reset/password_reset_form.html",
            success_url="password_reset_email_confirm",
            email_template_name="accounts/password_reset/password_reset_email.html",
            form_class=PwdResetForm,), name="pwdreset", ),

    path("password_reset_confirm/<uidb64>/<token>",auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset/password_reset_confirm.html",
            success_url="password_reset_complete/",

            form_class=PwdResetConfirmForm,),name="password_reset_confirm"),
    path("password_reset/password_reset_email_confirm/",TemplateView.as_view(template_name="accounts/password_reset/reset_status.html"),
        name="password_reset_done" ),

    path("password_reset_confirm/Mg/password_reset_complete/",TemplateView.as_view(template_name="accounts/password_reset/reset_status.html"),
        name="password_reset_complete"),

   ####################################################################################################
  
   # Custom views
    path('register/', views.register_view, name='register'), 
    path('logged_out/', logged_out_view, name='logged_out'),
    path('update_profile_picture/', views.update_profile_picture, name='update_profile_picture'),

     path('common_search/', views.common_search, name='common_search'),
]