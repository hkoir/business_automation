
from django.urls import path
from .import views


app_name = 'core'


urlpatterns = [
    path('', views.home, name='home'),
    path('core_dashboard/', views.core_dashboard, name='core_dashboard'),
    path('view_employee/', views.view_employee, name='view_employee'),

    # path('add_employee/', views.add_employee, name='add_employee'),
    # path('update_employee/<int:employee_id>/', views.update_employee, name='update_employee'),
    # path('delete_employee/<int:employee_id>/', views.delete_employee, name='delete_employee'),


    path('manage_department/', views.manage_department, name='manage_department'),
    path('update_department/<int:id>/', views.manage_department, name='update_department'),
    
    path('manage_position/', views.manage_position, name='manage_position'),
    path('update_position/<int:id>/', views.manage_position, name='update_position'),
  
    path('create_employee/', views.manage_employee, name='create_employee'),
    path('update_employee/<int:id>/', views.manage_employee, name='update_employee'),
    path('delete_employee/<int:id>/', views.manage_employee, {'delete': True}, name='delete_employee'),
    path('employee_list/', views.employee_list, name='employee_list'),

  
    path('create_company/', views.manage_company, name='create_company'),
    path('update_company/<int:id>/', views.manage_company, name='update_company'),
    path('delete_company/<int:id>/', views.manage_company, name='delete_company'),

    path('create_location/', views.manage_location, name='create_location'),
    path('update_location/<int:id>/', views.manage_location, name='update_location'),
    path('delete_location/<int:id>/', views.manage_location, {'delete': True}, name='delete_location'),
     
     
     path('add_notice/', views.add_notice, name='add_notice'), 
     path('view_notices/', views.view_notices, name='view_notices'),  
     path('all_qc/', views.all_qc, name='all_qc'),


      path('view_attendance/', views.view_attendance, name='view_attendance'),
      path('attendance_input/', views.attendance_input, name='attendance_input'),
      path('update_attendance/<int:employee_id>/', views.update_attendance, name='update_attendance'),     
     
      path('create_salary/', views.create_salary, name='create_salary'),
      path('download_salary/', views.download_salary, name='download_salary'),

      path('view_employee_changes/', views.view_employee_changes, name='view_employee_changes'),
      path('download_employee_changes/', views.download_employee_changes, name='download_employee_changes'),

      path('view_employee_changes_single/<int:employee_id>/', views.view_employee_changes_single, name='view_employee_changes_single'),
      
      path('generate_pay_slip/<int:employee_id>/', views.generate_pay_slip, name='generate_pay_slip'),    
      path('generate_salary_certificate/<int:employee_id>/', views.generate_salary_certificate, name='generate_salary_certificate'),
      path('generate_experience_certificate/<int:employee_id>/', views.generate_experience_certificate, name='generate_experience_certificate'),

   

]