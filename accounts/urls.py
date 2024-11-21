
from . import views
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import logged_out_view  



app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:logged_out'), name='logout'),

    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # Custom views
    path('register/', views.register_view, name='register'),
    path('', views.home, name='home'),
    path('logged_out/', logged_out_view, name='logged_out'),
    path('update_profile_picture/', views.update_profile_picture, name='update_profile_picture'),
]