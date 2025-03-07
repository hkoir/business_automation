
from django import forms
from django.contrib.auth.models import User

from product.models import Product,Category
from.models import PurchaseRequestOrder,PurchaseRequestItem, QualityControl
from inventory.models import Warehouse,Location
from supplier.models import Supplier
from purchase.models import PurchaseRequestOrder,PurchaseOrder
from django.contrib.auth.models import User

from accounts.models import CustomUser
from.models import Batch


class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        exclude=['user','remaining_quantity']

        widgets={
            'manufacture_date':forms.DateInput(attrs={'type':'date'}),
            'expiry_date':forms.DateInput(attrs={'type':'date'})
        }



class AssignRolesForm(forms.Form):
    requester = forms.ModelChoiceField(queryset=CustomUser.objects.all(), label="Requester")
    reviewer = forms.ModelChoiceField(queryset=CustomUser.objects.all(), label="Reviewer")
    approver = forms.ModelChoiceField(queryset=CustomUser.objects.all(), label="Approver")


class PurchaseRequestForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequestOrder  
        fields = ['category', 'product', 'product_type', 'quantity']  

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Category",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label="Product",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    product_type = forms.ChoiceField(
        choices=[
            ('raw_materials', 'Raw Materials'),
            ('finished_product', 'Finished Product'),
            ('component', 'Component'),
            ('BOM', 'BOM')
        ],
        label="Product Type",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantity = forms.IntegerField(
        label="Quantity",
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder  
        fields = ['purchase_request_order', 'status', 'supplier']  

    purchase_request_order = forms.ModelChoiceField(
        queryset=PurchaseRequestOrder.objects.all(),
        label="Purchase Request Order",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    order_item_id = forms.ModelChoiceField(
        queryset=PurchaseRequestItem.objects.all(),
        required=False)

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Category",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label="Product",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    product_type = forms.ChoiceField(
        choices=[
            ('raw_materials', 'Raw Materials'),
            ('finished_product', 'Finished Product'),
            ('component', 'Component'),
            ('BOM', 'BOM')
        ],
        label="Product Type",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    quantity = forms.IntegerField(
        label="Quantity",
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    def __init__(self, *args, request_instance=None, **kwargs):
        super(PurchaseOrderForm, self).__init__(*args, **kwargs)

        if request_instance:  
            self.fields['purchase_request_order'].queryset = PurchaseRequestOrder.objects.filter(id=request_instance.id)
            self.fields['order_item_id'].queryset = PurchaseRequestItem.objects.filter(purchase_request_order=request_instance)
            purchase_request_item = PurchaseRequestItem.objects.filter(purchase_request_order=request_instance).first()
            if purchase_request_item:
                self.fields['quantity'].initial = purchase_request_item.quantity 
            if purchase_request_item and purchase_request_item.product:
                product = purchase_request_item.product
                self.fields['product'].initial = product 
               
        else:
            self.fields['purchase_request_order'].queryset = PurchaseRequestOrder.objects.all()
            self.fields['order_item_id'].queryset = PurchaseRequestItem.objects.all()

        self.fields['purchase_request_order'].widget.attrs.update({
            'style': 'max-width: 200px; word-wrap: break-word; overflow: hidden; text-overflow: ellipsis;'
        })
          
        self.fields['order_item_id'].widget.attrs.update({
            'style': 'max-width: 200px; word-wrap: break-word; overflow: hidden; text-overflow: ellipsis;'
        })


class QualityControlForm(forms.ModelForm):
    comments = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control custom-textarea',
                'rows': 5, 
                'style': 'height: 100px;',  
            }
        )
    )
    inspection_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    class Meta:
        model = QualityControl
        fields = ['total_quantity','good_quantity', 'bad_quantity','inspection_date', 'comments']

    def clean(self):
        cleaned_data = super().clean()
        total_quantity = cleaned_data.get("total_quantity")
        good_quantity = cleaned_data.get("good_quantity")
        bad_quantity = cleaned_data.get("bad_quantity")
        
        if good_quantity and bad_quantity and total_quantity:
            if good_quantity + bad_quantity > total_quantity:
                raise forms.ValidationError("Good and bad quantities cannot exceed the total quantity.")
        return cleaned_data

class PurchaseOrderSearchForm(forms.Form):
    order_number = forms.CharField(
        label="Purchase Order Number",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter order number'})
    )


class PurchaseStatusForm(forms.Form):
    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('REVIEWED', 'Reviewed'),
        ('APPROVED', 'Approved'),
        ('CANCELLED', 'Cancelled'),
    ]
    approval_status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select)

    remarks = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control custom-textarea',
                'rows': 5, 
                'style': 'height: 100px;',  
            }
        ),
        required=False
    )
