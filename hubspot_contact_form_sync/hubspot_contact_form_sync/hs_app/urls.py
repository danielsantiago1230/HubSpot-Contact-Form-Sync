from django.urls import path
from hubspot_contact_form_sync.hs_app.views import HelloWorldView

app_name = "hs_app"

urlpatterns = [
    path("hello/", HelloWorldView.as_view(), name="hello_world"),
]
