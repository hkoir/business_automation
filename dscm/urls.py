
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path("accounts/", include("django.contrib.auth.urls")),
    path('',include('core.urls',namespace='core')),
    path('logistics/',include('logistics.urls',namespace='logistics')),
    path('manufacture/',include('manufacture.urls',namespace='manufacture')),
    path('product/',include('product.urls',namespace='product')),
    path('purchase/',include('purchase.urls',namespace='purchase')),
    path('sales/',include('sales.urls',namespace='sales')),
    path('supplier/',include('supplier.urls',namespace='supplier')),
    path('inventory/',include('inventory.urls',namespace='inventory')),
    path('finance/',include('finance.urls',namespace='finance')),
    path('shipment/',include('shipment.urls',namespace='shipment')),
    path('reporting/',include('reporting.urls',namespace='reporting')),
    path('customer/',include('customer.urls',namespace='customer')),
    path('repairreturn/',include('repairreturn.urls',namespace='repairreturn')),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
