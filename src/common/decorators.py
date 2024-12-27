from django.conf import settings

from common.base_models import TenantIsolationMixIn
from common.base_serializers import BaseTenantSerializer


def tenant_isolation_view(cls):
    """
    What this decorator does is:
    - Inject BaseTenantSerializer to serializer_class attribute if exists
    - Inject BaseTenantSerializer to result of get_serializer_class method if exists
    - checks if the model of serializer is inherited from TenantIsolationMixIn
    - adds attribute _is_tenant_isolation_view_injected to class to be used by middleware
    """
    def check_serializer_model(serializer_klass):
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
    if origin_get_serializer_class:
        def get_serializer_class(self):
            serializer_cls = origin_get_serializer_class(self)
            if not issubclass(serializer_cls, BaseTenantSerializer):
                return mix_serializer_cls(serializer_cls)
            return serializer_cls

        cls.get_serializer_class = get_serializer_class
    return cls
