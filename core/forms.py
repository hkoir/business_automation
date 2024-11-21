from django import forms
from.models import Employee,Company,Location




class AddEmployeeForm(forms.ModelForm):
    joining_date = forms.DateField(label='joining_date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Employee
        exclude = ['user','resignation_date','employee_code','bonus','gross_monthly_salary','house_allowance','medical_allowance','transportation_allowance','updated_at'] 
 
 

class AddCompanyForm(forms.ModelForm):      
    class Meta:
        model = Company
        exclude = ['created_at','updated_at','history','user']



   # address = forms.CharField(
    #     widget=forms.Textarea(
    #         attrs={
    #             'class': 'form-control custom-textarea',
    #             'rows': 4, 
    #             'style': 'height: 20px;', 
    #         }
    #     )
    # )


class AddLocationForm(forms.ModelForm):  
    class Meta:
        model=Location
        fields = ['company','name','phone']




class UpdateLocationForm(forms.ModelForm):
    address = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control custom-textarea',
                'rows': 3, 
                'style': 'height: 30px;', 
            }
        )
    )
    class Meta:
        model=Location
        exclude = ['location_id','history','created_at','updated_at','user']



from.models import Notice,AttendanceModel

class NoticeForm(forms.ModelForm):

    content=forms.CharField(widget=(
        forms.Textarea(attrs={
            'class':'form-control custom-textarea',
            'rows':3,
            'style':'height:200px'
        })
    ))
    class Meta:
        model = Notice
        exclude =['created_at']




class AttendanceForm(forms.ModelForm):
    class Meta:
        model = AttendanceModel
        exclude=['total_hours']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)      
        self.fields['date'].widget = forms.DateInput(attrs={'type':'date'})   
        self.fields['check_in_time'].widget = forms.TimeInput(attrs={'type':'time'})   
        self.fields['check_out_time'].widget = forms.TimeInput(attrs={'type':'time'})   
        


class EditAttendanceForm(forms.ModelForm):
    class Meta:
        model = AttendanceModel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)      
        self.fields['date'].widget = forms.DateInput(attrs={'type':'date'})   
        self.fields['check_in_time'].widget = forms.TimeInput(attrs={'type':'time'})   
        self.fields['check_out_time'].widget = forms.TimeInput(attrs={'type':'time'})   
        


class MonthYearForm(forms.Form):
    month = forms.IntegerField(min_value=1, max_value=12)
    year = forms.IntegerField(min_value=2000, max_value=2700)
