from django.conf import settings
from django.core.management import call_command
from django.db.models import loading
from django.test import TestCase


class TestCase(TestCase):
    apps = ('chronicler.tests', )

    def _pre_setup(self):
        # Add the models to the db.
        self._original_installed_apps = list(settings.INSTALLED_APPS)
        settings.INSTALLED_APPS = list(settings.INSTALLED_APPS)
        for app in self.apps:
            settings.INSTALLED_APPS.append(app)
        loading.cache.loaded = False
        call_command('syncdb', interactive=False, verbosity=0, migrate=False)
        # Call the original method that does the fixtures etc.
        super(TestCase, self)._pre_setup()

    def _post_teardown(self):
        # Call the original method.
        super(TestCase, self)._post_teardown()
        # Restore the settings.
        settings.INSTALLED_APPS = self._original_installed_apps
        loading.cache.loaded = False


from test_create_audit import TestCreateAudit
from test_audit_decorator import TestCreateAuditEntry
