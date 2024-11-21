
from django import forms
from .models import ReturnOrRefund
from sales.models import SaleOrder


class ReturnOrRefundForm(forms.ModelForm):
    remarks = forms.CharField( required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control custom-textarea',
                'rows': 3,  
                'style': 'height: 50px;width:250px',  
            },
           
        )
    )       

    class Meta:
        model = ReturnOrRefund
        fields = ['sale','return_reason','refund_type','quantity_refund']

    def __init__(self, *args, **kwargs):
        sale_order_id = kwargs.pop('sale_order_id', None)
        super(ReturnOrRefundForm, self).__init__(*args, **kwargs)
        if sale_order_id:
            self.fields['sale'].queryset = SaleOrder.objects.filter(sale_order__id=sale_order_id)
       


# below form is for updating by user/path('manage_return_request/<int:return_id>/', views.manage_return_request, name='manage_return_request'),
class ReturnOrRefundFormInternal(forms.ModelForm):
    processed_date = forms.DateField(
        label='Processed date',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    class Meta:
        model = ReturnOrRefund
        exclude = ['created_at','updated_at','product','customer','warehouse','location','quantity_sold' ]
    

from django import forms
from .models import FaultyProduct
from django import forms
from .models import Replacement

class FaultyProductForm(forms.ModelForm):
    class Meta:
        model = FaultyProduct
        exclude = ['created_at','updated_at','sale','warehouse','location','product','faulty_product_quantity','customer_feedback' ]
        widgets = {
            'reason_for_fault': forms.Textarea(attrs={'rows': 3}),
            'inspection_date': forms.DateInput(attrs={'type': 'date'}),
            'resolution_date': forms.DateInput(attrs={'type': 'date'}),
            'resolution_action': forms.Textarea(attrs={'rows': 2}),
        }


class ReplacementProductForm(forms.ModelForm):
    class Meta:
        model = Replacement
        fields = ['source_inventory','warehouse','location','quantity','status','user']  



