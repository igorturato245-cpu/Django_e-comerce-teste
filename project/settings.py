import os
import sentry_sdk
from pathlib import Path
from celery.schedules import crontab
from sentry_sdk.integrations.django import DjangoIntegration

BASE_DIR = Path(__file__).resolve().parent.parent

# 1. Tenta carregar o local_settings no topo para usar as variáveis
try:
    from . import local_settings
except ImportError:
    raise Exception("O arquivo local_settings.py é obrigatório para rodar a aplicação.")

# Segurança vinda do local_settings
SECRET_KEY = local_settings.SECRET_KEY
DEBUG = getattr(local_settings, 'DEBUG', False) # Padrão é False para segurança
ALLOWED_HOSTS = getattr(local_settings, 'ALLOWED_HOSTS', [])

# PagSeguro
PAGSEGURO_EMAIL = getattr(local_settings, 'PAGSEGURO_EMAIL', None)
PAGSEGURO_TOKEN = getattr(local_settings, 'PAGSEGURO_TOKEN', None)
PAGSEGURO_SANDBOX = getattr(local_settings, 'PAGSEGURO_SANDBOX', True)
PAGSEGURO_NOTIFICATION_URL = getattr(local_settings, 'PAGSEGURO_NOTIFICATION_URL', None)
PAGSEGURO_REDIRECT_URL = getattr(local_settings, 'PAGSEGURO_REDIRECT_URL', None)
PAGSEGURO_LOG_IN_MODEL = getattr(local_settings, 'PAGSEGURO_LOG_IN_MODEL', False)

# ERP
ERP_API_URL = getattr(local_settings, 'ERP_API_URL', None)
ERP_API_KEY = getattr(local_settings, 'ERP_API_KEY', None)
ERP_CLIENT_ID = getattr(local_settings, 'ERP_CLIENT_ID', None)
ERP_CLIENT_SECRET = getattr(local_settings, 'ERP_CLIENT_SECRET', None)
ERP_REFRESH_TOKEN = getattr(local_settings, 'ERP_REFRESH_TOKEN', None)
ERP_LOJA_ID =  getattr(local_settings, 'ERP_LOJA_ID', None)

URL_GOOGLE_SHEETS=getattr(local_settings,'URL_GOOGLE_SHEETS', None)


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'e_comerce',
    'pagamentos',
    'carrinho',
    'cadastro_de_usuarios',
    'institucional',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'base_templates', BASE_DIR /'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'e_comerce.views.context_processors.google_ads_ids',
                # CORREÇÃO: Garante que a variável 'debug' chegue nos templates
                'django.template.context_processors.debug', 
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

# Database (Prioriza o que estiver no local_settings)
DATABASES = getattr(local_settings, 'DATABASES', {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
})

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# CACHE EM PRODUÇÃO (Usa Redis para ser compatível com Celery)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": getattr(local_settings, 'REDIS_URL', "redis://127.0.0.1:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Celery
CELERY_BROKER_URL = getattr(local_settings, 'CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Sao_Paulo'

CELERY_BEAT_SCHEDULE = {
    'verificar-rastreio-a-cada-hora': {
        'task': 'pagamentos.tasks.check_all_orders_tracking_task',
        'schedule': crontab(minute=0)
    },
    'limpar-carrinhos-diariamente': {
        'task': 'carrinho.tasks.limpar_carrinhos_abandonados_task',
        'schedule': crontab(hour=3, minute=0)
    }
}

# Internationalization
LANGUAGE_CODE = 'pt-BR'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# E-mail (Configurações reais)
EMAIL_BACKEND = getattr(local_settings, 'EMAIL_BACKEND', "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = getattr(local_settings, 'EMAIL_HOST', "smtp.zoho.com")
EMAIL_PORT = getattr(local_settings, 'EMAIL_PORT', 587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = getattr(local_settings, 'EMAIL_HOST_USER', "")
EMAIL_HOST_PASSWORD = getattr(local_settings, 'EMAIL_HOST_PASSWORD', "")
DEFAULT_FROM_EMAIL = "contato@luviahome.com.br"

# Estáticos e Media
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'base_static']
STATIC_ROOT = BASE_DIR / 'static'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Sessões
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7 # 1 semana
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

GOOGLE_ANALYTICS_ID=getattr(local_settings,'GOOGLE_ANALYTICS_ID',"")
GOOGLE_TAG_ID=getattr(local_settings,'GOOGLE_TAG_ID',"")
CODIGO_ENVIO_GOOGLE_TAG_CARRINHO=getattr(local_settings,'CODIGO_ENVIO_GOOGLE_TAG_CARRINHO',"")
CODIGO_ENVIO_GOOGLE_TAG_CHECKOUT=getattr(local_settings,'CODIGO_ENVIO_GOOGLE_TAG_CHECKOUT',"")
CODIGO_ENVIO_GOOGLE_TAG_PAGAMENTO=getattr(local_settings,'CODIGO_ENVIO_GOOGLE_TAG_PAGAMENTO',"")
CODIGO_ENVIO_GOOGLE_TAG_INDEX=getattr(local_settings,'CODIGO_ENVIO_GOOGLE_TAG_INDEX',"")

# --- SEGURANÇA DE PRODUÇÃO (HTTPS) ---
if not DEBUG:
    CSRF_TRUSTED_ORIGINS = getattr(local_settings, 'CSRF_TRUSTED_ORIGINS', [])
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # HSTS
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Sentry Init
SENTRY_DSN = getattr(local_settings, 'SENTRY_DSN', None)
if SENTRY_DSN and not DEBUG:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
       integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True
    )