
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

from sales.models import SaleQualityControl

class QualityControlFormByCustomer(forms.ModelForm):  

    class Meta:
        model = SaleQualityControl
        fields = ['total_quantity', 'good_quantity_by_customer', 'bad_quantity_by_customer', 'inspection_date_by_customer', 'comments_by_customer']
        widgets={
            'inspection_date_by_customer':forms.DateInput(attrs={'type':'date'}),
            'comments_by_customer':forms.Textarea(attrs={
                'class':'form-control',
                'row':2,
                'style':'height:100px',
                'placeholder':'Please enter your comment'
            }),
           

        }
