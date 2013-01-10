import os
get_path = lambda *args: os.path.join(os.path.dirname(__file__), *args)

import sys
sys.path.append(os.path.dirname(__file__))

TEMPLATE_DEBUG = DEBUG = True
DATABASES = {
    'default':
        {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/django_checkio_voting.db'
        }
}
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = '/tmp/django_checkio_voting.db'
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.messages',
    'testapp',
    'voting'
    )

TEMPLATE_DIRS = (
    get_path('templates'),
    )

ROOT_URLCONF = 'test_project.urls'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    )

#overriting voting.settings
VOTING_REDIRECT_VIEW_DEFAULT_URL = '/main-page/'
VOTING_REDIRECT_VIEW_THANKS_MESSAGE = 'You are the best :)'