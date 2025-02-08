
from django.urls import path
from .import views


app_name = 'commonapp'


urlpatterns = [
    path('common_view/', views.common_view, name='common_view'),
    

]