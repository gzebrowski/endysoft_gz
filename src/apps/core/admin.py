from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from apps.core.models import (Customer, Department, Organization, Tenant,
                              TenantUser)
from common.admin_utils import AdminRequestFormMixIn


@admin.register(TenantUser)
class TenantUserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "tenant",
    ]
    raw_id_fields = ("user", "tenant")


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "domain", "organizations", "departments", "customers", "created_at", "updated_at"]
    search_fields = ["name", "domain"]
    list_filter = ["created_at", "updated_at"]
    readonly_fields = ["created_at", "updated_at"]

    def organizations(self, obj):
        return format_html(
            '<a href="{}?tenant_id={}">organizations</a>',
            reverse("admin:core_organization_changelist"),
            obj.pk,
        )

    def departments(self, obj):
        return format_html(
            '<a href="{}?tenant_id={}">departments</a>',
            reverse("admin:core_department_changelist"),
            obj.pk,
        )

    def customers(self, obj):
        return format_html(
            '<a href="{}?tenant_id={}">customers</a>',
            reverse("admin:core_customer_changelist"),
            obj.pk,
        )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "created_at", "updated_at"]
    search_fields = ["name"]
    list_filter = ["created_at", "updated_at"]
    readonly_fields = ["created_at", "updated_at", "tenant_id"]


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "organization", "created_at", "updated_at"]
    search_fields = ["name"]
    list_filter = ["created_at", "updated_at"]
    readonly_fields = ["created_at", "updated_at", "tenant_id"]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "department", "email", "phone", "created_at", "updated_at"]
    search_fields = ["name", "email"]
    list_filter = ["created_at", "updated_at"]
    readonly_fields = ["created_at", "updated_at", "tenant_id"]
