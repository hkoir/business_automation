
from django import forms
from .models import  TicketCustomerFeedback

class TicketCustomerFeedbackForm(forms.ModelForm):
    class Meta:
        model =  TicketCustomerFeedback
        exclude=['feedback_id']
        widgets={
            'comments':forms.Textarea(attrs={
                'class':'form-control',
                'row':2,
                'style':'height:100px',
                'placeholder':'Please enter your comment'
            }),
           
        }
      


class FilterForm(forms.Form):
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

 
    ticket_number = forms.CharField(
        label='Ticket Number',
        required=False,
       
    )   