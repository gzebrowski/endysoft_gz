from rest_framework.routers import DefaultRouter

from apps.core.views import (CustomerView, DepartmentView, OrganizationView,
                             TenantView)
from apps.users.views import UsersViewSet

router = DefaultRouter()

router.register("users", UsersViewSet, basename="users_url")
router.register("tenants", TenantView, basename="tenants_url")
router.register("organizations", OrganizationView, basename="organizations_url")
router.register(r"departments/(?P<organization>\d+)", DepartmentView, basename="departments_url")
router.register(r"customers/(?P<department>\d+)", CustomerView, basename="customers_url")

urlpatterns = router.urls
