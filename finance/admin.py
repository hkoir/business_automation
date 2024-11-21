from django.contrib import admin

from.models import PurchaseInvoice,PurchasePayment,SaleInvoice,SalePayment

admin.site.register(PurchaseInvoice)
admin.site.register(PurchasePayment)
admin.site.register(SaleInvoice)
admin.site.register(SalePayment)
