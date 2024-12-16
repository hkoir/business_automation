from django import forms
from.models import Employee,Company,Location,Department,Position



class ManageDepartmentForm(forms.ModelForm):   
    description = forms.CharField(required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control custom-textarea',
                'rows': 4, 
                'style': 'height: 20px;', 
            }
        )
    )
    custom_department_name = forms.CharField(
        max_length=100,
        required=False,
        label=" Enter Custom Department",
        help_text="Add a new department if it does not exist in the choices."
    )

    class Meta:
        model = Department
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False  



class ManagePositionForm(forms.ModelForm):
    description = forms.CharField(required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control custom-textarea',
                'rows': 4, 
                'style': 'height: 20px;', 
            }
        )
    )
    custom_position_name = forms.CharField(
        max_length=100,
        required=False,
        label="Enter Custom Position",
        help_text="Add a new position if it does not exist in the current department."
    )

    class Meta:
        model = Position
        fields = ['department', 'name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.all()
        self.fields['name'].required = False  
       



class AddEmployeeForm(forms.ModelForm):
    joining_date = forms.DateField(label='joining_date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Employee
        exclude = ['user','user_profile','resignation_date','employee_code','bonus','gross_monthly_salary','house_allowance','medical_allowance','transportation_allowance','updated_at'] 
 
 

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









from product.models import Product,Category
from finance.models import PurchaseInvoice,SaleInvoice
from logistics.models import PurchaseShipment,SaleShipment
from repairreturn.models import Replacement,ReturnOrRefund,FaultyProduct  
from manufacture.models import MaterialsRequestOrder
from operations.models import OperationsRequestOrder,ExistingOrder
from purchase.models import PurchaseOrder, PurchaseRequestOrder
from inventory.models import InventoryTransaction,Warehouse,TransferOrder
from sales.models import SaleOrder,SaleRequestOrder



class CommonFilterForm(forms.Form):
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

 
    ID_number = forms.CharField(
        label='Order ID',
        required=False,
       
    )   

    warehouse_name = forms.ModelChoiceField(queryset=Warehouse.objects.all(),required=False)
    product_name = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_product_name'}),
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_category'}),
    )

    employee_name = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_employee_name'}),
    )
           
    purchase_request_order_id = forms.ModelChoiceField(
        queryset=PurchaseRequestOrder.objects.all(),
        required=False,        
        widget=forms.Select(attrs={'id': 'id_purchase_request_order_id'}),)
    
    purchase_order_id = forms.ModelChoiceField(
        queryset=PurchaseOrder.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_purchase_order_id'}),)
    
    purchase_shipment_id = forms.ModelChoiceField(
        queryset=PurchaseShipment.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_purchase_shipment_id'}),)
    
    purchase_invoice_id = forms.ModelChoiceField(
        queryset=PurchaseInvoice.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_purchase_invoice_id'}),)
    

    sale_request_order_id = forms.ModelChoiceField(
        queryset=SaleRequestOrder.objects.all(),
        required=False,        
        widget=forms.Select(attrs={'id': 'id_sale_request_order_id'}),)
    
    sale_order_id = forms.ModelChoiceField(
        queryset=SaleOrder.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_sale_order_id'}),)
    
    
    sale_shipment_id = forms.ModelChoiceField(
        queryset=SaleShipment.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_sale_shipment_id'}),)
    
    sale_invoice_id = forms.ModelChoiceField(
        queryset=SaleInvoice.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_sale_invoice_id'}),)
    
    transfer_id = forms.ModelChoiceField(
        queryset=TransferOrder.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_transfer_id'}),)
    
    return_refund__id = forms.ModelChoiceField(
        queryset=ReturnOrRefund.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_return_id'}),)
    
    materials_order_id = forms.ModelChoiceField(
        queryset=MaterialsRequestOrder.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_materials_order_id'}),)
   
    operations_request_order_id = forms.ModelChoiceField(
        queryset=OperationsRequestOrder.objects.all(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_operations_request_order_id'}),)
   



