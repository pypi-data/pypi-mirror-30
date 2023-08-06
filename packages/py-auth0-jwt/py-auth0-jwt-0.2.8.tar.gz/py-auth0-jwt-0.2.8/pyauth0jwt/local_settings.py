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

AUTH0_DOMAIN = 'mtmcduffie.auth0.com'
AUTH0_CLIENT_ID = 'y16slzzzDr9jKhEHsZZmKYskQdJKoMFm'
AUTH0_SECRET = '4Dj1gBxhJPxq2XueUwgp0TCNcCtWLjhmixX-prtNEKz8p-vdTRI7ew3U4F7-wyfw'
AUTH0_CALLBACK_URL = 'http://localhost:8001/login/callback_handling/'
AUTH0_SUCCESS_URL = '/login/landingpage/'
AUTH0_LOGOUT_URL = 'https://mtmcduffie.auth0.com/v2/logout?returnTo=http://localhost:8001/login/auth'