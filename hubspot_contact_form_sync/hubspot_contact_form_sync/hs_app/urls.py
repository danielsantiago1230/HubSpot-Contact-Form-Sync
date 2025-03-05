from django.urls import path
from hubspot_contact_form_sync.hs_app.views import ContactFormView, contact_success, ContactListView, ContactUpdateView
from django.urls import reverse_lazy

app_name = "hs_app"

urlpatterns = [
    path('contact/', ContactFormView.as_view(), name='contact_form'),
    path('contact/success/', contact_success, name='contact_success'),
    path('contacts/', ContactListView.as_view(), name='contact_list'),
    path('contact/<str:contact_id>/update/', ContactUpdateView.as_view(), name='contact_update'),
]