"""
Django settings for biohub project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from biohub.utils import path

# Essential paths
BIOHUB_DIR = path.modpath('biohub')
BIOHUB_MAIN_DIR = path.modpath('biohub.main')
BIOHUB_CORE_DIR = path.modpath('biohub.core')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!pe+q_5_8#!3qyvrdo4=j4j_$+$4wz@$1q^o#t9xrdqveq(=#_'

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'biohub.core',
    'biohub.accounts',
    'biohub.notices',
    'biohub.core.files',
    'biohub.core.plugins',
    'haystack',
    'biohub.biobrick',
    'biohub.biocircuit',
    'biohub.forum',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'biohub.main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'NAME': 'notices',
        'OPTIONS': {
            'autoescape': False,
            'builtins': ['biohub.notices.template.filters']
        }
    }
]

WSGI_APPLICATION = 'main.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'biohub.accounts.validators.PasswordValidator'
    }
]

# Overwrite default User model.
AUTH_USER_MODEL = 'accounts.User'

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
    }
}

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
    'PAGE_SIZE': 30,
    'DEFAULT_AUTHENTICATION_CLASSES': ('biohub.utils.rest.authentication.NoCSRFAuthentication',)
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'asgi_redis.RedisChannelLayer',
        'ROUTING': 'biohub.core.channel_routing.channels_routing',
        'CONFIG': {
            'hosts': [],
            'symmetric_encryption_keys': [SECRET_KEY],
        }
    }
}

EMAIL_USE_SSL = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_TIMEOUT = 10

# Extra configurations

from biohub.core.conf import settings as biohub_settings  # noqa:E402

DATABASES['default'].update(biohub_settings.DEFAULT_DATABASE)
INSTALLED_APPS += biohub_settings.BIOHUB_PLUGINS[:]
TIME_ZONE = biohub_settings.TIMEZONE
MEDIA_ROOT = biohub_settings.UPLOAD_DIR

if biohub_settings.SECRET_KEY:
    SECRET_KEY = SECRET_KEY

if biohub_settings.REDIS_URI:
    CHANNEL_LAYERS['default']['CONFIG']['hosts'].append(
        biohub_settings.REDIS_URI)
    CHANNEL_LAYERS['default']['TEST_CONFIG'] = {
        'hosts': [biohub_settings.REDIS_URI],
        'symmetric_encryption_keys': [SECRET_KEY],
    }

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": biohub_settings.REDIS_URI,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }

    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"
else:
    CHANNEL_LAYERS['default']['BACKEND'] = 'asgiref.inmemory.ChannelLayer'
    del CHANNEL_LAYERS['default']['CONFIG']

if biohub_settings.EMAIL:
    mail_conf = biohub_settings.EMAIL

    EMAIL_HOST = mail_conf['HOST']
    EMAIL_HOST_USER = mail_conf['HOST_USER']
    EMAIL_HOST_PASSWORD = mail_conf['HOST_PASSWORD']
    EMAIL_PORT = mail_conf['PORT']

    del mail_conf

del biohub_settings

# tmp
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'products',
        'INCLUDE_SPELLING': True,
    },
}
