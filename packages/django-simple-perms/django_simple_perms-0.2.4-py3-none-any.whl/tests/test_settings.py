DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'testing',
        'SUPPORTS_TRANSACTIONS': False,
    },
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'tests.test_app',
    'simple_perms',
)

AUTHENTICATION_BACKENDS = (
    'simple_perms.backend.PermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)


SECRET_KEY = "secret"
