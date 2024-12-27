from rest_framework import serializers

from apps.core.models import (Customer, Department, Organization, Tenant,
                              TenantUser)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("name", "details")


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ("name", "details")


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ("name", "email", "phone")


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ("domain", "name")

    def create(self, validated_data):
        tenant = Tenant.objects.create(**validated_data)
        TenantUser.objects.create(
            tenant=tenant,
            user=self.context["request"].user,
        )
        return tenant
