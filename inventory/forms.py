
from django import forms
from.models import InventoryTransaction,Warehouse,Location,TransferItem
from product.models import Product




class AddWarehouseForm(forms.ModelForm):      
    class Meta:
        model = Warehouse
        exclude = ['created_at','updated_at','history','user','description','warehouse_id','reorder_level','lead_time']

class AddLocationForm(forms.ModelForm):      
    class Meta:
        model = Location
        fields= ['warehouse','name']



class InventoryTransactionForm  (forms.ModelForm):
    feedback = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control custom-textarea',
                'rows': 3,
                'style': 'height: 40px;', 
            }
        )
    )
    class Meta:
        model = InventoryTransaction
        exclude = ['user','created_at','updated_at','history']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),            
        }



class QualityControlCompletionForm(forms.Form):
    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        label="Select Warehouse",
        required=True
    )
    location = forms.ModelChoiceField(
        queryset=Location.objects.none(),  # Initially empty, will be dynamically loaded
        label="Select Location",
        required=True
    )  

    def __init__(self, *args, **kwargs):
        # Accept a 'warehouse' argument to filter location choices
        warehouse = kwargs.pop('warehouse', None)
        super().__init__(*args, **kwargs)
        
        if warehouse:
            self.fields['location'].queryset = Location.objects.filter(warehouse=warehouse)



class TransferProductForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all())
    source_warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.all())
    target_warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.all())
    source_location = forms.ModelChoiceField(queryset=Location.objects.all())
    target_location = forms.ModelChoiceField(queryset=Location.objects.all())
    quantity = forms.IntegerField(min_value=1)

    remarks = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control custom-textarea',
                'rows': 3,
                'style': 'height: 40px;', 
            }
        )
    )

    class Meta:
        model=TransferItem
        exclude=['transfer_order','user']

    
