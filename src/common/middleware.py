from django.conf import settings
from django.http import JsonResponse

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
        request.tenant_id = tenant.pk if tenant else None
        request.tenant = tenant
        tenant_required = False
        view_class = getattr(view_func, 'cls', None)
        if view_class and hasattr(view_class, '_is_tenant_isolation_view_injected'):
            tenant_required = True
        if tenant_required and not tenant:
            return JsonResponse({"error": "Tenant not found"}, status=400)
