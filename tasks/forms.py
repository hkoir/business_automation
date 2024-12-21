from django import forms
from .models import Task, Team, Employee
from django import forms
from .models import Task, User
from.models import TeamMember
from .models import QualitativeEvaluation
from core.models import Employee,Department,Position



class TaskAssignmentForm(forms.ModelForm):  
     due_dattime = forms.DateTimeField(label='Due datetime', required=False, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))   
     team_name = forms.CharField(label='Team name',required=False)
     member = forms.CharField(required=False)
     class Meta:
        model = Task
        fields = ['title', 'priority', 'assigned_to', 'due_datetime']  

     assigned_to = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        label="assigned to",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
     


class TeamForm(forms.ModelForm):
    description = forms.CharField(required=False,
    widget=forms.Textarea(
        attrs={
            'class': 'form-control custom-textarea',
            'rows': 3, 
            'style': 'height: 70px;',  
            }
        )
    )
    class Meta:
        model = Team
        fields = ['department','name','manager']

class AddMemberForm(forms.ModelForm):
    team = forms.ModelChoiceField(queryset=Team.objects.all(), required=True, label='Team')
    member = forms.ModelChoiceField(queryset=Employee.objects.all(), required=True, label='Member')
    class Meta:
        model = TeamMember
        fields = ['team','member','is_team_leader']



class TaskForm(forms.ModelForm):
    due_datetime = forms.DateTimeField(label='Due datetime', required=False, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))   
    assigned_to = forms.ChoiceField(
        choices=[('team', 'Team'), ('member', 'Member')],
        required=True,
        label='Assigned To'
    )

    remarks = forms.CharField(required=False,
    widget=forms.Textarea(
        attrs={
            'class': 'form-control custom-textarea',
            'rows': 3, 
            'style': 'height: 70px;',  
            }
        )
    )

    class Meta:
        model = Task
        fields = ['title', 'assigned_to', 'assigned_to_employee', 'assigned_to_team','task_manager','assigned_number', 'due_datetime','priority','remarks']


    def clean(self):
        cleaned_data = super().clean()
        assigned_to = cleaned_data.get('assigned_to')
        assigned_to_employee = cleaned_data.get('assigned_to_employee')
        assigned_to_team = cleaned_data.get('assigned_to_team')

        if assigned_to == 'team' and not assigned_to_team:
            raise forms.ValidationError('Please select a team for the task.')
        if assigned_to == 'member' and not assigned_to_employee:
            raise forms.ValidationError('Please select a member for the task.')
        
        return cleaned_data

   


class TaskProgressForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['progress']
        widgets = {
            'progress': forms.NumberInput(attrs={
                'min': 0,
                'max': 100,
                'class': 'form-control',
                'placeholder': 'Enter progress percentage (0-100)',
            })
        }

    def clean_progress(self):
        progress = self.cleaned_data['progress']
        if progress < 0 or progress > 100:
            raise forms.ValidationError("Progress must be between 0 and 100.")
        return progress



class RequestExtensionForm(forms.Form):
    extension_datetime = forms.DateTimeField(widget=forms.DateInput(attrs={'type': 'datetime-local'}), label="Requested Extension Date")
   

class ApproveExtensionForm(forms.Form):
    approve_choices = [('yes', 'Yes'), ('no', 'No')]
    approve = forms.ChoiceField(choices=approve_choices, widget=forms.RadioSelect, label="Approve Extension?")
    approval_datetime = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), label="Extended Datetime")
   
    comments = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}), required=False, label="Manager Comments")




class QualitativeEvaluationForm(forms.ModelForm):
    class Meta:
        model = QualitativeEvaluation
        fields = [
            'performance_evaluation', 
            'employee', 
            'task', 
            'evaluator',
            'manager_given_quantitative_number',
            'work_quality_score',
            'communication_quality_score',
            'teamwork_score',
            'initiative_score',
            'punctuality_score',
            'feedback'
        ]
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Add feedback here'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)     
        self.fields['task'].label = "Task Title"
        if 'initial' in kwargs and isinstance(kwargs['initial'].get('task'), Task):
            self.fields['task'].initial = kwargs['initial']['task'].title

    def clean(self):
        cleaned_data = super().clean()
        score_fields = [
            'work_quality_score',
            'communication_quality_score',
            'teamwork_score',
            'initiative_score',
            'punctuality_score'
        ]
        for field in score_fields:
            score = cleaned_data.get(field)
            if score < 0 or score > 5:
                self.add_error(field, f"{field.replace('_', ' ').capitalize()} must be between 0 and 5.")
        return cleaned_data




class YearlyTrendForm(forms.Form):  
    start_year = forms.IntegerField(label='Start Year',required=True)
    end_year = forms.IntegerField(label='End Year',required=True)           

    employee_name = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_employee_name'}),
    )
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),  # Fetch all departments
        label='Department',
        required=False,
        widget=forms.Select(
            attrs={
                'style': 'width: 200px;',  # Inline style for width
                'class': 'custom-select',  # Optional styling
            }
        ),
    )

    position = forms.ModelChoiceField(
        queryset=Position.objects.all(),  # Fetch all departments
        label=Position,
        required=False,
        widget=forms.Select(
            attrs={
                'style': 'width: 200px;',  # Inline style for width
                'class': 'custom-select',  # Optional styling
            }
        ),
    )




class MonthlyQuarterlyTrendForm(forms.Form):  
    year = forms.IntegerField(required=True, label="Year") 

    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        required=True,
        widget=forms.Select(attrs={'id': 'id_employee_name'}),
    )
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),  # Fetch all departments
        label='Department',
        required=False,
        widget=forms.Select(
            attrs={
                'style': 'width: 200px;',  # Inline style for width
                'class': 'custom-select',  # Optional styling
            }
        ),
    )

    position = forms.ModelChoiceField(
        queryset=Position.objects.all(),  # Fetch all departments
        label=Position,
        required=False,
        widget=forms.Select(
            attrs={
                'style': 'width: 200px;',  # Inline style for width
                'class': 'custom-select',  # Optional styling
            }
        ),
    )


class GroupTrendForm(forms.Form):  

    start_date = forms.DateField(
        label='Start Date',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    end_date = forms.DateField(
        label='End Date',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    days = forms.IntegerField(
        label='Number of Days',
        min_value=1,
        required=False
    )
   
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),  # Fetch all departments
        label='Department',
        required=False,
        widget=forms.Select(
            attrs={
                'style': 'width: 200px;',  # Inline style for width
                'class': 'custom-select',  # Optional styling
            }
        ),
    )

    position = forms.ModelChoiceField(
        queryset=Position.objects.all(),  # Fetch all departments
        label=Position,
        required=False,
        widget=forms.Select(
            attrs={
                'style': 'width: 200px;',  # Inline style for width
                'class': 'custom-select',  # Optional styling
            }
        ),
    )
