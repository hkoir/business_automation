

from pathlib import Path
import os
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-wzlf*t+-g32z73ia4=qdcbq*-2wkw_elwd_^%m3iodhllt9t!1'

DEBUG = True

ALLOWED_HOSTS = ['*','192.168.0.150','localhost','company-1.localhost']




SHARED_APPS = [
    'django_tenants',  
    'django.contrib.contenttypes',  
    'django.contrib.sessions',     
    'django.contrib.messages',     
    'django.contrib.staticfiles',  
    'django_crontab',               
    'django_celery_beat',   
    'django.contrib.admin',    
    'django.contrib.auth',    
    'clients',   
]

TENANT_APPS = [ 
   
    'accounts',
    'logistics',
    'manufacture',
    'product',
    'purchase',
    'sales',
    'supplier',
    'inventory',
    'finance',
    'shipment',
    'reporting',
    'customer',
    'tasks',  
    'core',
    'repairreturn',
    'operations',
    'django_extensions', 
]


INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]


TENANT_MODEL = "clients.Client"  
TENANT_DOMAIN_MODEL = "clients.Domain"  
DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)
PUBLIC_SCHEMA_NAME = 'public'





MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', 
    'django.contrib.auth.middleware.AuthenticationMiddleware', 
    'django_tenants.middleware.TenantMiddleware',   
  
    'django.contrib.messages.middleware.MessageMiddleware',  
    'clients.middleware.TenantValidationMiddleware',      
    'clients.middleware.CustomGeneralPurposeMiddleWare',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
     
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]



ROOT_URLCONF = 'dscm.urls'

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
                'accounts.context_processors.user_info',
                'accounts.context_processors.notifications_context',
                'accounts.context_processors.tenant_schema',
            ],
        },
    },
]

WSGI_APPLICATION = 'dscm.wsgi.application'



DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': 'scmdatabase',  # your PostgreSQL database name
        'USER': 'postgres',      # the user you created for PostgreSQL
        'PASSWORD': 'Arafat_123',  # the password for your PostgreSQL user
        'HOST': 'localhost',    # default for local database
        'PORT': '5432',         # default PostgreSQL port
    }
}


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }




# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/


import os
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'error.log'),  # Save error logs to this file
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],  # Logs errors to file and console
            'level': 'ERROR',  # Log ERROR level and above
            'propagate': True,
        },
        'inventory': {  # Replace 'inventory' with your app's name
            'handlers': ['file', 'console'],  # Logs DEBUG and above for this app
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}



CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Use Redis as the broker
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")


LOGIN_REDIRECT_URL = '/accounts/tenant_expire_check/'
LOGIN_URL = 'accounts:login'
# LOGIN_URL = "/accounts/login/"



EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    # Add other backends if you have any
]


# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your_email@gmail.com'  
# EMAIL_HOST_PASSWORD = 'your_password'      

DEFAULT_FROM_EMAIL = 'noreply@ddealshop.com'  # Default sender email
