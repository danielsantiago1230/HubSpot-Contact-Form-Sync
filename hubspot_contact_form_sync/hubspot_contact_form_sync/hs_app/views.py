from django.conf import settings
from django.shortcuts import render, redirect
from django import forms
from django.views.generic.edit import FormView, UpdateView
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

# Hubspot
from hubspot import HubSpot
from hubspot.crm.contacts import (
    SimplePublicObjectInputForCreate,
    SimplePublicObjectInput,
)
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


# CRM API - Update Contact
def update_contact(contact_id, data):
    try:
        simple_public_object_input = SimplePublicObjectInput(
            properties={
                "email": data["email"],
                "firstname": data["first_name"],
                "lastname": data["last_name"],
                "phone": data["phone"],
            }
        )
        api_response = api_client.crm.contacts.basic_api.update(
            contact_id=contact_id, simple_public_object_input=simple_public_object_input
        )
        return api_response
    except ApiException as e:
        print("Exception when updating contact: %s\n" % e)
        raise  # Re-raise the exception so it can be handled in form_valid


# CRM API - Get Contact by ID
def get_contact(contact_id):
    try:
        api_response = api_client.crm.contacts.basic_api.get_by_id(
            contact_id=contact_id,
            properties=["email", "firstname", "lastname", "phone"],
        )
        return api_response
    except ApiException as e:
        print("Exception when getting contact: %s\n" % e)
        raise  # Re-raise the exception so it can be handled in the view


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


# Contact Update Form - Reusing the same fields as ContactForm
class ContactUpdateForm(ContactForm):
    # Hidden field to store the contact ID
    contact_id = forms.CharField(widget=forms.HiddenInput())


# Contact Form View
class ContactFormView(LoginRequiredMixin, FormView):
    template_name = "hs_app/contact_form.html"
    form_class = ContactForm
    success_url = reverse_lazy("hs_app:contact_success")
    login_url = '/admin/login/'

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
            error_message = "HubSpot API Error"

            # Try to extract a more meaningful error message from the response
            error_body = str(e)

            # Check for common error patterns
            if "already exists" in error_body.lower():
                # Extract just the relevant part about the contact already existing
                import re

                match = re.search(r'"message":"([^"]+)"', error_body)
                if match:
                    error_message = match.group(1)
                else:
                    error_message = "A contact with this email already exists."
            elif "CONFLICT" in error_body:
                error_message = "There was a conflict creating this contact. The email may already be in use."

            print(f"Exception when creating contact: {e}")
            form.add_error(None, error_message)
            return super().form_invalid(form)
        except Exception as e:
            error_message = "An error occurred while processing your request. Please try again later."
            print(f"Unexpected error when creating contact: {e}")
            form.add_error(None, error_message)
            return super().form_invalid(form)


# Contact Update View
class ContactUpdateView(LoginRequiredMixin, FormView):
    template_name = "hs_app/contact_update.html"
    form_class = ContactUpdateForm
    success_url = reverse_lazy("hs_app:contact_list")
    login_url = '/admin/login/'

    def get_initial(self):
        # Get contact ID from URL
        contact_id = self.kwargs.get("contact_id")
        if not contact_id:
            raise Http404("Contact not found")

        try:
            # Fetch contact data from HubSpot
            contact = get_contact(contact_id)

            # Initialize form with contact data
            return {
                "contact_id": contact_id,
                "first_name": contact.properties.get("firstname", ""),
                "last_name": contact.properties.get("lastname", ""),
                "email": contact.properties.get("email", ""),
                "phone": contact.properties.get("phone", ""),
            }
        except ApiException as e:
            # If contact not found or API error
            if "not found" in str(e).lower():
                raise Http404("Contact not found")
            raise  # Re-raise other API exceptions

    def form_valid(self, form):
        # Process the form data here
        contact_id = form.cleaned_data["contact_id"]
        data = {
            "first_name": form.cleaned_data["first_name"],
            "last_name": form.cleaned_data["last_name"],
            "email": form.cleaned_data["email"],
            "phone": form.cleaned_data["phone"],
        }

        # Update data in HubSpot
        try:
            update_contact(contact_id, data)
            return super().form_valid(form)
        except ApiException as e:
            error_message = "HubSpot API Error"

            # Try to extract a more meaningful error message from the response
            error_body = str(e)

            # Check for common error patterns
            if "already exists" in error_body.lower():
                # Extract just the relevant part about the contact already existing
                import re

                match = re.search(r'"message":"([^"]+)"', error_body)
                if match:
                    error_message = match.group(1)
                else:
                    error_message = "A contact with this email already exists."
            elif "not found" in error_body.lower():
                error_message = "Contact not found. It may have been deleted."
            elif "CONFLICT" in error_body:
                error_message = "There was a conflict updating this contact. The email may already be in use."

            print(f"Exception when updating contact: {e}")
            form.add_error(None, error_message)
            return super().form_invalid(form)
        except Exception as e:
            error_message = "An error occurred while processing your request. Please try again later."
            print(f"Unexpected error when updating contact: {e}")
            form.add_error(None, error_message)
            return super().form_invalid(form)


@login_required(login_url='/admin/login/')
def contact_success(request):
    return render(request, "hs_app/contact_success.html")


# Contact List View
class ContactListView(LoginRequiredMixin, TemplateView):
    template_name = "hs_app/contact_list.html"
    login_url = '/admin/login/'

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
                limit=page_size, after=after_cursor,
                properties=["email", "firstname", "lastname", "phone", "createdate"]
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
