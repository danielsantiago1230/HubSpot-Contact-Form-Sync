import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "hubspot_contact_form_sync.users"
    verbose_name = _("Users")

    def ready(self):
        with contextlib.suppress(ImportError):
            import hubspot_contact_form_sync.users.signals  # noqa: F401
