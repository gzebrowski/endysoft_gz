# from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet


from drf_spectacular.utils import extend_schema

from apps.core.models import Customer, Department, Organization
from apps.core.serializers import (CustomerSerializer, DepartmentSerializer,
                                   OrganizationSerializer, TenantSerializer)
from common.decorators import tenant_isolation_view

from rest_framework.generics import GenericAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.mixins import (CreateModelMixin, ListModelMixin, RetrieveModelMixin,
                                   UpdateModelMixin, DestroyModelMixin)
# from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ViewSet, ViewSetMixin


class AppCommonView(ModelViewSet):
    pass


class TenantView(AppCommonView):
    permission_classes = [IsAuthenticated]
    serializer_class = TenantSerializer


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


@extend_schema(request=DepartmentSerializer)
@tenant_isolation_view
class DepartmentView(AppCommonView):
    queryset = Department.objects
    serializer_class = DepartmentSerializer
