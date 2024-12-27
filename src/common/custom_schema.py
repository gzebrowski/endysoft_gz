from django.conf import settings
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import OpenApiParameter


class CustomSchema(AutoSchema):
    global_params = [
        OpenApiParameter(
            name=settings.TENANT_HEADER,
            type=str,
            location=OpenApiParameter.HEADER,
            description="enter tenant domain",
        )
    ]

    def get_override_parameters(self):
        params = super().get_override_parameters()
        if settings.TENANT_DETECT_METHOD == "header":
            return params + self.global_params
        return params
