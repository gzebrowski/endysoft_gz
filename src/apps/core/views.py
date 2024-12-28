from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.core.models import Customer, Department, Organization, Tenant
from apps.core.serializers import (CustomerSerializer, DepartmentSerializer,
                                   OrganizationSerializer, TenantSerializer)
from common.decorators import tenant_isolation_view


class AppCommonView(ModelViewSet):
    pass


class TenantView(AppCommonView):
    permission_classes = [IsAuthenticated]
    serializer_class = TenantSerializer
    queryset = Tenant.objects

    def get_queryset(self):
        return self.queryset.filter(tenantuser__user=self.request.user)


@extend_schema(request=OrganizationSerializer)
@tenant_isolation_view
class OrganizationView(AppCommonView):
    queryset = Organization.objects
    serializer_class = OrganizationSerializer


@extend_schema(request=CustomerSerializer)
@tenant_isolation_view
class CustomerView(AppCommonView):
    queryset = Customer.objects
    serializer_class = CustomerSerializer

    def perform_create(self, serializer):
        serializer.save(department_id=self.kwargs.get("department"))

    def get_queryset(self):
        return self.queryset.filter(department_id=self.kwargs.get("department"))


@extend_schema(request=DepartmentSerializer)
@tenant_isolation_view
class DepartmentView(AppCommonView):
    queryset = Department.objects
    serializer_class = DepartmentSerializer

    def perform_create(self, serializer):
        serializer.save(organization_id=self.kwargs.get("organization"))

    def get_queryset(self):
        return self.queryset.filter(organization_id=self.kwargs.get("organization"))
