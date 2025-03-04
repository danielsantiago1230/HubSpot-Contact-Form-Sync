from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter
from django.urls import path, include

from hubspot_contact_form_sync.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)


app_name = "api"
urlpatterns = router.urls

# Add hs_app URLs
urlpatterns += [
    path("hs_app/", include("hubspot_contact_form_sync.hs_app.urls", namespace="hs_app")),
]
