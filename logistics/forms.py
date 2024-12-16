
from django import forms
from .models import PurchaseShipment,SaleShipment,PurchaseDispatchItem,SaleDispatchItem
from purchase.models import PurchaseOrderItem
from sales.models import SaleOrder,SaleOrderItem




class PurchaseShipmentForm(forms.ModelForm):
    estimated_delivery = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    class Meta:
        model = PurchaseShipment
        fields = ['carrier', 'tracking_number', 'estimated_delivery']




class SaleShipmentForm(forms.ModelForm):
    estimated_delivery = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    class Meta:
        model = SaleShipment
        fields = ['carrier', 'tracking_number', 'estimated_delivery','sales_order']

    def __init__(self, *args, sale_order=None, **kwargs):
        super(SaleShipmentForm, self).__init__(*args, **kwargs)
        if sale_order:
            self.fields['sales_order'].queryset = SaleOrder.objects.filter(id=sale_order.id)
        else:
            self.fields['sales_order'].queryset = SaleOrder.objects.all()



class PurchaseDispatchItemForm(forms.ModelForm):
    dispatch_date=forms.DateField(
        widget=forms.DateInput(attrs={'type':'date'}),
        required=False
    )
    delivery_date=forms.DateField(
        widget=forms.DateInput(attrs={'type':'date'}),
        required=False
    )

    class Meta:
        model = PurchaseDispatchItem
        exclude=['dispatch_id','user']


    def __init__(self, *args, purchase_shipment=None, **kwargs):
        super(PurchaseDispatchItemForm, self).__init__(*args, **kwargs)

        if purchase_shipment:
            self.fields['purchase_shipment'].queryset = PurchaseShipment.objects.filter(id=purchase_shipment.id)            
            self.fields['dispatch_item'].queryset = PurchaseOrderItem.objects.filter(purchase_order__purchase_shipment=purchase_shipment)
        else:
            self.fields['purchase_shipment'].queryset = PurchaseShipment.objects.all()
            self.fields['dispatch_item'].queryset = PurchaseOrderItem.objects.all()
         
        self.fields['purchase_shipment'].widget.attrs.update({
            'style': 'max-width: 200px; word-wrap: break-word; overflow: hidden; text-overflow: ellipsis;'
        })
          
        self.fields['dispatch_item'].widget.attrs.update({
            'style': 'max-width: 200px; word-wrap: break-word; overflow: hidden; text-overflow: ellipsis;'
        })



class SaleDispatchItemForm(forms.ModelForm):
    dispatch_date=forms.DateField(
        widget=forms.DateInput(attrs={'type':'date'}),
        required=False
    )
    delivery_date=forms.DateField(
        widget=forms.DateInput(attrs={'type':'date'}),
        required=False
    )

    class Meta:
        model = SaleDispatchItem
        exclude=['dispatch_id']


    def __init__(self, *args, sale_shipment=None, **kwargs):
        super(SaleDispatchItemForm, self).__init__(*args, **kwargs)

        if sale_shipment:
            self.fields['sale_shipment'].queryset = SaleShipment.objects.filter(id=sale_shipment.id)            
            self.fields['dispatch_item'].queryset = SaleOrderItem.objects.filter(sale_order__sale_shipment=sale_shipment)
        else:
            self.fields['sale_shipment'].queryset = SaleShipment.objects.all()
            self.fields['dispatch_item'].queryset = SaleOrderItem.objects.all()
         
        self.fields['sale_shipment'].widget.attrs.update({
            'style': 'max-width: 200px; word-wrap: break-word; overflow: hidden; text-overflow: ellipsis;'
        })
          
        self.fields['dispatch_item'].widget.attrs.update({
            'style': 'max-width: 200px; word-wrap: break-word; overflow: hidden; text-overflow: ellipsis;'
        })