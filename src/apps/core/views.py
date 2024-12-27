from django.shortcuts import get_object_or_404
# from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.core.serializers import (CustomerSerializer, DepartmentSerializer,
                                   OrganizationSerializer, TenantSerializer)
from common.decorators import tenant_isolation_view


class AppCommonView(ModelViewSet):
    def get_object(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])


class TenantView(AppCommonView):
    permission_classes = [IsAuthenticated]
    serializer_class = TenantSerializer


@tenant_isolation_view
class CustomerView(AppCommonView):
    serializer_class = CustomerSerializer


@tenant_isolation_view
class DepartmentView(AppCommonView):
    serializer_class = DepartmentSerializer


@tenant_isolation_view
class OrganizationView(AppCommonView):
    serializer_class = OrganizationSerializer
