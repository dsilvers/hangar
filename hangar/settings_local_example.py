import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []


PUSHER_APP_ID = ''
PUSHER_APP_KEY = ''
PUSHER_APP_SECRET = ''


# Temperatures go stale after 15 minutes
TEMPERATURE_STALENESS = 15*60

