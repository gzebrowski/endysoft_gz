from django.conf import settings
from rest_framework.exceptions import PermissionDenied

from apps.core.models import Tenant
from common.middleware_base import BaseMiddleware


class DetectTenantMiddleware(BaseMiddleware):
    def process_view(self, request, view_func, *args, **kwargs):
        if settings.TENANT_DETECT_METHOD == 'host':
            host = request.get_host()
            key = host.split('.')[0]
        else:
            key = request.headers.get(settings.TENANT_HEADER)
        tenant = Tenant.objects.filter(domain=key).first()
        request.tenant = tenant
        view_class = getattr(view_func, '__class__', None)
        if tenant and view_class and hasattr(view_class, '_is_tenant_isolation_view_injected'):
            if not request.user.is_staff:
                if not request.user.is_authenticated or not tenant.check_user(request.user):
                    raise PermissionDenied("Tenant mismatch")
