from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django_tenants.utils import get_tenant_model
from django.core.exceptions import PermissionDenied

User = get_user_model()

class TenantAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if request is None:
            return None

        tenant = getattr(request, 'tenant', None)
        if tenant is None:
            return None

        try:
            user = User.objects.get(username=username, tenant=tenant)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        