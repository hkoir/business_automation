from django.db import models
from django.contrib.auth.models import User 
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords
import uuid


from logistics.models import PurchaseShipment,SaleShipment
from purchase.models import PurchaseOrder
from sales.models import SaleOrder
from purchase.models import PurchaseOrder 
from django.db.models import Sum




class PurchaseInvoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='purchase_invoice_user')
    purchase_shipment = models.ForeignKey(PurchaseShipment, related_name='shipment_invoices', on_delete=models.CASCADE,null=True,blank=True)
    invoice_number = models.CharField(max_length=150, unique=True, blank=True, null=True)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20,null=True,blank=True,
            choices=[
                ('SUBMITTED','Submitted'),
                 ('FULLY_PAID','Fully Paid'),
                 ('PARTIALLY_PAID','Partially Paid')
            ])
    
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2,blank=True, null=True)
    issued_date = models.DateTimeField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

   
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"PINV-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_number
    
    @property
    def total_paid_amount(self):
        return self.purchase_payment_invoice.aggregate(Sum('amount'))['amount__sum'] or 0

    @property
    def is_fully_paid(self):
        total_paid = self.purchase_payment_invoice.aggregate(Sum('amount'))['amount__sum'] or 0
        return total_paid >= self.amount_due
    @property
    def remaining_balance(self):
        total_paid = self.purchase_payment_invoice.aggregate(Sum('amount'))['amount__sum'] or 0
        return self.amount_due - total_paid




class PurchasePayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='purchase_payment_user')
    purchase_invoice = models.ForeignKey(PurchaseInvoice, related_name='purchase_payment_invoice', on_delete=models.CASCADE, null=True, blank=True) 
    payment_id =models.CharField(max_length=20, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=[
        ('CASH', 'Cash'), 
        ('CREDIT', 'Credit Card'), 
        ('BANK', 'Bank Transfer')
    ])

    status = models.CharField(max_length=20,null=True,blank=True,
            choices=[
                ('IN_PROCESS','In Process'),
                ('FULLY_PAID','Fully Paid'),
                 ('PARTIALLY_PAID','Partially Paid')
            ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = f"PPAYID-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment of {self.amount} for Purchase Order {self.purchase_invoice.invoice_number}"
    
    @property
    def is_fully_paid(self):
        total_invoice = self.purchase_invoice.aggregate(Sum('amount_due'))['amount_due__sum'] or Decimal(0)
        tolerance = Decimal('0.01')  
        return abs(total_invoice - self.amount) <= tolerance 



############ sales ##############################################################
from decimal import Decimal

class SaleInvoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='sale_invoice_user')
    sale_shipment = models.ForeignKey(SaleShipment, related_name='sale_shipment_invoices', on_delete=models.CASCADE,null=True,blank=True)
    invoice_number = models.CharField(max_length=150, unique=True, blank=True, null=True)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2,blank=True, null=True)
    issued_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20,null=True,blank=True,
            choices=[
                ('SUBMITTED','Submitted'),
                 ('FULLY_PAID','Fully Paid'),
                 ('PARTIALLY_PAID','Partially Paid')
            ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()


    @property
    def is_fully_paid(self):
        total_paid = self.sale_payment_invoice.aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        tolerance = Decimal('0.01')  
        return abs(total_paid - self.amount_due) <= tolerance 
    @property
    def remaining_balance(self):
        total_paid = self.sale_payment_invoice.aggregate(Sum('amount'))['amount__sum'] or 0
        return self.amount_due - total_paid



    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"SINV-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_number


class SalePayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='sale_payment_user')
    sale_invoice = models.ForeignKey(SaleInvoice, related_name='sale_payment_invoice', on_delete=models.CASCADE, null=True, blank=True) 
    payment_id =models.CharField(max_length=20, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=[
        ('CASH', 'Cash'), 
        ('CREDIT', 'Credit Card'), 
        ('BANK', 'Bank Transfer')
    ])

    status = models.CharField(max_length=20,null=True,blank=True,
            choices=[
                ('IN_PROCESS','IN Process'),
                 ('FULLY_PAID','Fully Paid'),
                 ('PARTIALLY_PAID','Partially Paid')
            ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = f"SPAYID-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment of {self.amount} for Sale Order {self.sale_invoice.invoice_number}"
    

    
    @property
    def is_fully_paid(self):
        total_invoice = self.sale_invoice.aggregate(Sum('amount_due'))['amount_due__sum'] or Decimal(0)
        tolerance = Decimal('0.01')  
        return abs(total_invoice - self.amount) <= tolerance 