import pytest
from django.apps import AppConfig
from django.conf import settings
from django.utils.module_loading import import_module, import_string
from rest_framework.test import APIClient


'''
This code below just search for all installed apps and import the app_conftest.py file and then 
import all fixtures from it to the global scope. This way, you can use the fixtures in your tests
'''
app_list = []
for app in settings.INSTALLED_APPS:
    if not app.startswith("apps."):
        continue
    app_mod = import_string(app)
    if AppConfig in getattr(app_mod, "mro", lambda: [])():
        app_list.append(app_mod.name)
    else:
        app_list.append(app)

for app in app_list:
    app_conftest_mod = ".".join([app, "app_conftest"])
    try:
        cnf_mod = import_module(app_conftest_mod)
    except ImportError:
        pass
    else:
        for attr in dir(cnf_mod):
            item = getattr(cnf_mod, attr)
            # all functions decorated with @pytest.fixture has attribute _pytestfixturefunction. So we know
            # that this is a fixture
            if hasattr(item, "_pytestfixturefunction"):
                globals()[attr] = item


@pytest.fixture
def api_client():
    return APIClient()
