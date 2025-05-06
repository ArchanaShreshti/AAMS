from django.contrib.admin.apps import AdminConfig
from django.contrib.auth.apps import AuthConfig
from django.contrib.contenttypes.apps import ContentTypesConfig
from django.apps import AppConfig


class MongoAdminConfig(AdminConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoAuthConfig(AuthConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoContentTypesConfig(ContentTypesConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"

class MongoAdminCustomConfig(AppConfig):
    name = 'AAMS.apps'  # Update the name attribute
    label = 'mongo_admin_custom'