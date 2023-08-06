import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "TEST")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles'
]

AUTH0_DOMAIN = ''
AUTH0_CLIENT_ID = ''
AUTH0_SECRET = ''
AUTH0_CALLBACK_URL = ''
AUTH0_SUCCESS_URL = ''
AUTH0_LOGOUT_URL = ''
