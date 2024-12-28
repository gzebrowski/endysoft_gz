from django.conf import settings
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView

from common.base_models import TenantIsolationMixIn
from common.base_serializers import BaseTenantSerializer


def tenant_isolation_view(cls: APIView):
    """
    What this decorator does is:
    - Inject BaseTenantSerializer to serializer_class attribute if exists
    - Inject BaseTenantSerializer to result of get_serializer_class method if exists
    - Inject get_queryset method to filter queryset by tenant_id if model has tenant_id field
    - Inject initial method to check if user is staff or tenant is matched
    - checks if the model of serializer is inherited from TenantIsolationMixIn
    - adds attribute _is_tenant_isolation_view_injected to class to be used by middleware
    """
    def check_serializer_model(serializer_klass):
        """
        Just for validation purposes in debug mode
        """
        if settings.DEBUG:
            meta_cls = getattr(serializer_klass, 'Meta', None)
            if meta_cls:
                model = meta_cls.model
                if not issubclass(model, TenantIsolationMixIn):
                    raise ValueError(f"{model} must inherit from TenantIsolationMixIn")
        return serializer_klass

    def mix_serializer_cls(origin_cls):
        class Serializer(origin_cls, BaseTenantSerializer):
            pass
        return check_serializer_model(Serializer)

    _is_tenant_isolation_view_injected = getattr(cls, '_is_tenant_isolation_view_injected', False)
    if _is_tenant_isolation_view_injected:
        return cls
    cls._is_tenant_isolation_view_injected = True
    _serializer_class = getattr(cls, 'serializer_class', None)
    if _serializer_class and not issubclass(_serializer_class, BaseTenantSerializer):
        cls.serializer_class = mix_serializer_cls(_serializer_class)

    origin_get_serializer_class = getattr(cls, 'get_serializer_class', None)
    origin_get_queryset = getattr(cls, 'get_queryset', None)

    def get_queryset(self):
        queryset = origin_get_queryset(self)
        if hasattr(queryset.model, 'tenant_id'):
            return queryset.filter(tenant_id=self.request.tenant_id)
        return queryset

    cls.get_queryset = get_queryset

    if origin_get_serializer_class:
        def get_serializer_class(self):
            """
            Inject BaseTenantSerializer to the result of get_serializer_class method
            """
            serializer_cls = origin_get_serializer_class(self)
            if not issubclass(serializer_cls, BaseTenantSerializer):
                return mix_serializer_cls(serializer_cls)
            return serializer_cls

        cls.get_serializer_class = get_serializer_class

    orig_initial_request = getattr(cls, 'initial', None)

    def initial(self, request, *args, **kwargs):
        """
        We override initial method of views.APIView because it is the first point that the request object is fully
        initialized (ie it has the user object after authentication). We check if the user is staff or the tenant is
        matched with the user. If not we raise PermissionDenied
        """
        orig_initial_request(self, request, *args, **kwargs)
        if not request.user.is_staff:
            tenant = getattr(request, 'tenant', None)
            if not request.user.is_authenticated or not tenant or not tenant.check_user(request.user):
                raise PermissionDenied("Tenant mismatch")
        return request

    cls.initial = initial

    return cls
