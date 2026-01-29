"""
Fichier de configuration Django pour le projet CertiSign.
"""

import os
from pathlib import Path
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-0wqe6r=yxnp=j=3_eqvtz8u99vh3t=0rc!^m6@jtl0=wys*+ev')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['*']

# Optimisations pour éviter les timeouts et 502
# Timeout pour les connexions de base de données
DATABASE_CONNECTION_TIMEOUT = 60

# Configuration pour éviter les fermetures prématurées
CONN_MAX_AGE = 600  # 10 minutes de connexion persistante
OPTIONS = {
    'MAX_CONNS': 20,
    'CONN_HEALTH_CHECKS': True,
}

#ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,192.168.4.131', cast=Csv())

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_extensions',
    
    # Third-party apps
    'rest_framework',
    'corsheaders',
    'drf_yasg',
    'django_filters',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    
    # Local apps
    'users',
    'documents',
    'signature_templates',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'certisign_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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
]

WSGI_APPLICATION = 'certisign_project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='CertiSign_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='easysoft'),
        'HOST': config('DB_HOST', default='192.168.4.131'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,  # Connexions persistantes
        'OPTIONS': {
            'connect_timeout': 60,
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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

# Custom user model
AUTH_USER_MODEL = 'users.CustomUser'

# Email Configuration
# Configuration pour l'envoi d'emails
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Toujours utiliser SMTP pour envoyer réellement les emails
print("\n📫 Configuration d'envoi d'email réel activée - Les notifications seront envoyées à {}".format(config('SUPER_ADMIN_EMAIL', default='emmanuelyakam1@gmail.com')))

EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@certisign.com')

# Super Admin Email pour les notifications
SUPER_ADMIN_EMAIL = config('SUPER_ADMIN_EMAIL', default='emmanuelyakam1@gmail.com')

# URL de base pour les liens dans les emails - Maintenant via Nginx
BASE_URL = config('BASE_URL', default='https://ppd.camgovca.cm')

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS configuration - Mise à jour pour Nginx
CORS_ALLOWED_ORIGINS = [
    "https://ppd.camgovca.cm",        # Frontend via Nginx
    "https://127.0.0.1",           # Nginx local
    "http://127.0.0.1",            # Nginx local HTTP
]

CORS_ALLOW_CREDENTIALS = True

# CSRF configuration - Ajout des origines autorisées
CSRF_TRUSTED_ORIGINS = [
    "https://ppd.camgovca.cm",
    "https://127.0.0.1",
    "http://127.0.0.1",
]

# Configuration CSRF pour les cookies
CSRF_COOKIE_SECURE = True  # Cookies CSRF uniquement en HTTPS
CSRF_COOKIE_HTTPONLY = False  # Permettre l'accès JavaScript pour les frameworks frontend
CSRF_COOKIE_SAMESITE = 'Lax'  # Protection CSRF avec SameSite

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# Paramètres Simple JWT
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),      # 8 heures au lieu de 1
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),      # 7 jours au lieu de 1
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
}

JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Doc@uthANTIC",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Doc@uthANTIC",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "Doc@uthANTIC",

    # Welcome text on the login screen
    "welcome_sign": "Bienvenue sur le site d'administration de Doc@uthANTIC",

    # Logo to use for your site, must be present in static files, used for login form
    "site_logo": "img/doc.png",

    # Copyright on the footer
    "copyright": "ANTIC",

    # The model admin to search from the search bar, search bar omitted if excluded
    "search_model": ["users.CustomUser", "documents.Document"],
}