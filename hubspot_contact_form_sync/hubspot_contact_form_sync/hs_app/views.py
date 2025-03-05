from django.conf import settings
from django.shortcuts import render
from django import forms
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.urls import reverse_lazy

# Hubspot
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate
from hubspot.crm.contacts.exceptions import ApiException

# Configuring HubSpot client
api_client = HubSpot(access_token=settings.HUBSPOT_ACCESS_TOKEN)


# CRM API - Create Contact
def create_contact(data):
    try:
        simple_public_object_input_for_create = SimplePublicObjectInputForCreate(
            properties={
                "email": data["email"],
                "firstname": data["first_name"],
                "lastname": data["last_name"],
                "phone": data["phone"],
            }
        )
        api_response = api_client.crm.contacts.basic_api.create(
            simple_public_object_input_for_create=simple_public_object_input_for_create
        )
        return api_response
    except ApiException as e:
        print("Exception when creating contact: %s\n" % e)
        raise  # Re-raise the exception so it can be handled in form_valid


# Contact Form
class ContactForm(forms.Form):
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": " "}),
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": " "}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": " "}),
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": " "}),
    )


# Contact Form View
class ContactFormView(FormView):
    template_name = "hs_app/contact_form.html"
    form_class = ContactForm
    success_url = reverse_lazy("hs_app:contact_success")

    def form_valid(self, form):
        # Process the form data here
        data = {
            "first_name": form.cleaned_data["first_name"],
            "last_name": form.cleaned_data["last_name"],
            "email": form.cleaned_data["email"],
            "phone": form.cleaned_data["phone"],
        }

        # Send data to HubSpot
        try:
            create_contact(data)
            return super().form_valid(form)
        except ApiException as e:
            # Extract just the "Contact already exists" message if present
            error_message = "HubSpot API Error"
            if "Contact already exists" in str(e):
                error_message = "Contact already exists"
            else:
                error_message = f"HubSpot API Error: {e}"
            print(f"Exception when creating contact: {e}")
            form.add_error(None, error_message)
            return super().form_invalid(form)
        except Exception as e:
            error_message = "An error occurred while processing your request. Please try again later."
            print(f"Unexpected error when creating contact: {e}")
            form.add_error(None, error_message)
            return super().form_invalid(form)


def contact_success(request):
    return render(request, "hs_app/contact_success.html")


# Contact List View
class ContactListView(TemplateView):
    template_name = "hs_app/contact_list.html"

    def get(self, request, *args, **kwargs):
        # Reset pagination cursors if going back to page 1
        page = request.GET.get("page", 1)
        try:
            page = int(page)
        except ValueError:
            page = 1

        if page == 1:
            # Clear all pagination cursors from session when starting from page 1
            keys_to_remove = [
                key
                for key in request.session.keys()
                if key.startswith("contact_cursor_page_")
            ]
            for key in keys_to_remove:
                del request.session[key]

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get page number from query parameters, default to 1
        page = self.request.GET.get("page", 1)
        try:
            page = int(page)
            if page < 1:
                page = 1
        except ValueError:
            page = 1

        # Set page size (increased from 1 to a more reasonable value)
        page_size = 10

        # Get the cursor from session if available
        cursor_key = f"contact_cursor_page_{page}"
        after_cursor = self.request.session.get(cursor_key)

        try:
            # Get contacts with pagination
            contacts_page = api_client.crm.contacts.basic_api.get_page(
                limit=page_size, after=after_cursor
            )

            # Extract contacts from response
            contacts = contacts_page.results

            # Store cursors for pagination in session
            if (
                contacts_page.paging
                and contacts_page.paging.next
                and contacts_page.paging.next.after
            ):
                # Store the next cursor for the next page
                self.request.session[f"contact_cursor_page_{page + 1}"] = (
                    contacts_page.paging.next.after
                )

            # Calculate pagination info
            has_next = bool(
                contacts_page.paging
                and contacts_page.paging.next
                and contacts_page.paging.next.after
            )
            has_previous = page > 1

            context.update(
                {
                    "contacts": contacts,
                    "page": page,
                    "has_next": has_next,
                    "has_previous": has_previous,
                    "next_page": page + 1 if has_next else None,
                    "previous_page": page - 1 if has_previous else None,
                }
            )

        except ApiException as e:
            print(f"Exception when fetching contacts: {e}")
            context["error"] = f"HubSpot API Error: {e}"
        except Exception as e:
            print(f"Unexpected error when fetching contacts: {e}")
            context["error"] = (
                "An error occurred while fetching contacts. Please try again later."
            )

        return context
