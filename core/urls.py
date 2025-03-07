
from django.urls import path
from .import views


app_name = 'core'


urlpatterns = [
    path('home/', views.home, name='home'),
    path('', views.dashboard, name='dashboard'),
    path('core_dashboard/', views.core_dashboard, name='core_dashboard'),
    path('only_core_dashboard/', views.only_core_dashboard, name='only_core_dashboard'),
    path('view_employee/', views.view_employee, name='view_employee'),
    path('employee_list/', views.employee_list, name='employee_list'),
   
    path('manage_department/', views.manage_department, name='manage_department'),  
    path('manage_location/', views.manage_location, name='manage_location'),

    path('create_positionn/', views.manage_position, name='create_position'),    
    path('update_positionn/<int:id>/', views.manage_position, name='update_position'),    
    path('delete_position/<int:id>/', views.delete_position, name='delete_position'),  
    path('position_details/<int:id>/', views.position_details, name='position_details'),  

    path('create_job_requirement/', views.manage_job_requirement, name='create_job_requirement'),    
    path('update_job_requirement/<int:id>/', views.manage_job_requirement, name='update_job_requirement'),    
    path('delete_job_requirement/<int:id>/', views.delete_job_requirement, name='delete_job_requirement'),  

    path('create_job_description/', views.manage_job_description, name='create_job_description'),    
    path('update_job_description/<int:id>/', views.manage_job_description, name='update_job_description'),    
    path('delete_job_description/<int:id>/', views.delete_job_descriptiont, name='delete_job_description'),  

    path('create_company/', views.create_company, name='create_company'),
    path('update_company/<int:id>/', views.create_company, name='update_company'),
    path('delete_company/<int:id>/', views.delete_company,  name='delete_company'),    
    
    path('manage_employee/', views.manage_employee, name='manage_employee'),
    path('update_employee/<int:id>/', views.manage_employee, name='update_employee'),
    path('delete_employee/<int:id>/', views.delete_employee,  name='delete_employee'),    
            
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
    
    path('preview_pay_slip/<int:employee_id>/', views.preview_pay_slip, name='preview_pay_slip'),
    path('generate_and_send_pay_slip/<int:employee_id>/', views.generate_and_send_pay_slip, name='generate_and_send_pay_slip'),
        
    path('preview_salary_certificate/<int:employee_id>/', views.preview_salary_certificate, name='preview_salary_certificate'),
    path('generate_and_send_salary_certificate/<int:employee_id>/', views.generate_and_send_salary_certificate, name='generate_and_send_salary_certificate'),
          
    path('preview_experience_certificate/<int:employee_id>/', views.preview_experience_certificate, name='preview_experience_certificate'),
    path('generate_and_send_experience_certificate/<int:employee_id>/', views.generate_and_send_experience_certificate, name='generate_and_send_experience_certificate'),
      
    path('create_company_policy/', views.manage_company_policy, name='create_company_policy'),
    path('update_company_policy/<int:id>/', views.manage_company_policy, name='update_company_policy'),
    path('delete_company_policy/<int:id>/', views.delete_company_policy, name='delete_company_policy'),   

    path('create_salary_structure/', views.manage_salary_structure, name='create_salary_structure'),
    path('update_salary_structure/<int:id>/', views.manage_salary_structure, name='update_salary_structure'),
    path('delete_salary_structure/<int:id>/', views.delete_salary_structure, name='delete_salary_structure'),   
    
    path('create_festival/', views.manage_festival, name='create_festival'),
    path('update_festival/<int:id>/', views.manage_festival, name='update_festival'),
    path('delete_festival/<int:id>/', views.delete_festival, name='delete_festival'),   

    path('create_performance_bonus/', views.manage_performance_bonus, name='create_performance_bonus'),
    path('update_performance_bonus/<int:id>/', views.manage_performance_bonus, name='update_performance_bonus'),
    path('delete_performance_bonus/<int:id>/', views.delete_performance_bonus, name='delete_performance_bonus'),   

    path('create_leave_type/', views.manage_leave_type, name='create_leave_type'),
    path('update_leave_type/<int:id>/', views.manage_leave_type, name='update_leave_type'),
    path('delete_leave_type/<int:id>/', views.delete_leave_type, name='delete_leave_type'), 

    path('apply_leave/', views.apply_leave, name='apply_leave'),
    path('leave_history/', views.leave_history, name='leave_history'),
    path('pending_leave_list/', views.pending_leave_list, name='pending_leave_list'),
    path('approve_leave/<int:leave_id>/', views.approve_leave, name='approve_leave'),  
    path('leave_summary/', views.leave_summary, name='leave_summary'),
    path('leave_dashboard/', views.leave_dashboard, name='leave_dashboard'),

    path('carry-forward-leave/', views.carry_forward_leave, name='carry_forward_leave'),
    path('update_leave_balances_for_all/', views.monthly_leave_accrual_update, name='update_leave_balances_for_all'),
    path('check_and_deduct_late_leaves/', views.check_and_deduct_late_leaves, name='check_and_deduct_late_leaves'),

]