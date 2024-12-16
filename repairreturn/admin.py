from django.contrib import admin

from.models import Replacement,ReturnOrRefund,FaultyProduct,ScrappedItem,ScrappedOrder



admin.site.register(Replacement)
admin.site.register(ReturnOrRefund)
admin.site.register(FaultyProduct)

admin.site.register(ScrappedOrder)
admin.site.register(ScrappedItem)
