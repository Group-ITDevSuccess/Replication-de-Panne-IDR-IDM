"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 5.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
import django
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

if DEBUG:
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = 'django-insecure-gjb)aqi29250ow!0-x$47a!!sdm10g-*px77i%=2#=cvggmz8m'
else:
    SECRET_KEY = 'xotuff%dxqv7-7!(a9^gq@u6q&-sxs*p=3!pp5oxu0x%)&2x7i'

ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '127.0.0.1', '172.16.112.2', '41.188.27.242', 'suivie-panne.inviso-group.mg']

# Application definition

INSTALLED_APPS = [
    'import_export',
    'fontawesome_6',
    'admin_interface',
    'colorfield',
    "debug_toolbar",
    # "allauth",  # new
    # "allauth.account",  # new
    # "allauth.socialaccount",  # new
    # social providers
    # "allauth.socialaccount.providers.github",  # new
    # "allauth.socialaccount.providers.twitter",  # new
    'django.contrib.humanize',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'guard.apps.GuardConfig',
    'apps.idr_idm.apps.IdrIdmConfig',
    'django_browser_reload',

]


INTERNAL_IPS = [
    "127.0.0.1",
    "localhost"
]



X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    # 'allauth.account.middleware.AccountMiddleware',
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    'django_browser_reload.middleware.BrowserReloadMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.context_processors.context_processor_navbar'
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # <-- UPDATED line
        'NAME': 'suivie-idr',  # <-- UPDATED line
        'USER': 'root',  # <-- UPDATED line
        'PASSWORD': 'AllahSeul',  # <-- UPDATED line
        'HOST': '127.0.0.1',  # <-- UPDATED line
        'PORT': '3306',
    },
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# AUTHENTICATION_BACKENDS = (
#     "allauth.account.auth_backends.AuthenticationBackend",
# )
#
# SITE_ID = 1
# ACCOUNT_EMAIL_VERIFICATION = "none"
# LOGIN_REDIRECT_URL = "home"
# ACCOUNT_LOGOUT_ON_GET = True
#

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'fr-FR'

TIME_ZONE = 'Indian/Antananarivo'

USE_I18N = True
USE_L10N = True
USE_TZ = True

DATE_INPUT_FORMATS = ("%d/%m/%Y", "%Y-%m-%d")

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

if not DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static_files')
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
            "LOCATION": os.path.join(BASE_DIR, 'cache'),
        }
    }

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
USE_THOUSAND_SEPARATOR = True

if django.VERSION >= (4, 2):
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

SERVER_LDAP = 'ldap://ad-server-1'
DN_LDAP = "dc=smtp-group,dc=mg"

AUTH_USER_MODEL = 'guard.CustomUser'
