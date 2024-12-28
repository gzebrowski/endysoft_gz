from rest_framework import serializers

from apps.core.models import (Customer, Department, Organization, Tenant,
                              TenantUser)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name", "details")


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ("id", "name", "details")


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ("id", "domain", "name")

    def create(self, validated_data):
        tenant = Tenant.objects.create(**validated_data)
        TenantUser.objects.create(
            tenant=tenant,
            user=self.context["request"].user,
        )
        return tenant
