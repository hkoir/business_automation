
from django import forms
from .models import ReturnOrRefund
from sales.models import SaleOrder,SaleOrderItem   
from .models import FaultyProduct
from .models import Replacement




class ReturnOrRefundForm(forms.ModelForm):
    remarks = forms.CharField( required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control custom-textarea',
                'rows': 3,  
                'style': 'height: 30px;width:150px',  
            },
           
        )
    )      

    sale_order = forms.ModelChoiceField(
        queryset=SaleOrder.objects.none(),  
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
        )

    class Meta:
        model = ReturnOrRefund
        fields = ['sale','return_reason','refund_type','quantity_refund']

    def __init__(self, *args, **kwargs):
        sale_order_id = kwargs.pop('sale_order_id', None)
        super(ReturnOrRefundForm, self).__init__(*args, **kwargs)       
        if sale_order_id:
            self.fields['sale'].queryset = SaleOrderItem.objects.filter(sale_order_id=sale_order_id)
    
        self.fields['sale_order'].queryset = SaleOrder.objects.filter(id=sale_order_id)



class ReturnOrRefundFormInternal(forms.ModelForm):
    remarks = forms.CharField( required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control custom-textarea',
                'rows': 4,  
                'style': 'width:350px',  
            },
           
        )
    )  
    processed_date = forms.DateField(
        label='Processed date',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    class Meta:
        model = ReturnOrRefund
        exclude = ['created_at','updated_at','product','customer','warehouse','location','quantity_sold' ]


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



