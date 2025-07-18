# settings.py - CORREÇÃO PARA MYSQL 8.0+
import os
from pathlib import Path
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-fallback-key-only-for-emergency')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1', 
    '.railway.app',
    'sitedjangoenv4-production.up.railway.app',
    'mapaeleitoral.com.br',
    'www.mapaeleitoral.com.br'
]

# CSRF Protection
CSRF_TRUSTED_ORIGINS = [
    'https://mapaeleitoral.com.br',
    'https://www.mapaeleitoral.com.br',
    'https://sitedjangoenv4-production.up.railway.app',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mapa_eleitoral',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.gzip.GZipMiddleware',  # Compressão GZIP
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'siteDjango.urls'

# === CONFIGURAÇÕES DE TEMPLATES OTIMIZADAS ===
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# Cache de templates em produção
if not DEBUG:
    TEMPLATES[0]['APP_DIRS'] = False  # Desabilitar APP_DIRS quando usar loaders
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

WSGI_APPLICATION = 'siteDjango.wsgi.application'

# === CONFIGURAÇÃO DE BANCO DE DADOS OTIMIZADA ===
if config('DATABASE_URL', default=None):
    # Para produção (Railway, Heroku, etc.)
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL'),
            conn_max_age=3600,  # Aumentado para 1h
            conn_health_checks=True,
            ssl_require=config('DB_SSL', default=False, cast=bool)
        ),
        'blog': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'blog',
            'USER': config('DB_USER', default='root'),
            'PASSWORD': config('DB_PASSWORD', default='MHOyVWaRdBsIxajzheoDtesardXtYhmP'),
            'HOST': config('DB_HOST', default='gondola.proxy.rlwy.net'),
            'PORT': config('DB_PORT', default=29860, cast=int),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES', innodb_lock_wait_timeout=50",
                'charset': 'utf8mb4',
                'autocommit': True,
                'isolation_level': 'read committed',
            },
            'CONN_MAX_AGE': 3600,  # 1h
        }
    }
    # Otimizações específicas para produção
    DATABASES['default']['OPTIONS'] = {
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES', innodb_lock_wait_timeout=50",
        'charset': 'utf8mb4',
        'autocommit': True,
        'isolation_level': 'read committed',
    }
else:
    # Para desenvolvimento local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('DB_NAME', default='mapa_eleitoral'),
            'USER': config('DB_USER', default='root'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='3306'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
                'autocommit': True,
            },
            'CONN_MAX_AGE': 300,  # 5 minutos em dev
        },
        'blog': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'blog',
            'USER': config('DB_USER', default='root'),
            'PASSWORD': config('DB_PASSWORD', default='MHOyVWaRdBsIxajzheoDtesardXtYhmP'),
            'HOST': config('DB_HOST', default='gondola.proxy.rlwy.net'),
            'PORT': config('DB_PORT', default=29860, cast=int),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
                'autocommit': True,
            },
            'CONN_MAX_AGE': 300,  # 5 minutos em dev
        }
    }

# === DATABASE ROUTER ===
DATABASE_ROUTERS = ['siteDjango.db_router.DatabaseRouter']

# === CONFIGURAÇÕES DE CACHE SIMPLIFICADAS ===
# Usar cache em memória por padrão para evitar problemas
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'mapa-eleitoral-cache',
        'TIMEOUT': 3600 if not DEBUG else 300,  # 1h em prod, 5min em dev
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        }
    }
}

# Cache otimizado por ambiente
if not DEBUG and config('REDIS_URL', default=None):
    # Redis para produção
    try:
        import redis
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.redis.RedisCache',
                'LOCATION': config('REDIS_URL'),
                'OPTIONS': {
                    'CONNECTION_POOL_KWARGS': {
                        'max_connections': 50,
                        'retry_on_timeout': True,
                        'socket_keepalive': True,
                        'socket_keepalive_options': {},
                        'health_check_interval': 30,
                    },
                    'IGNORE_EXCEPTIONS': True,
                    'PARSER_CLASS': 'redis.connection.HiredisParser',
                },
                'KEY_PREFIX': 'mapaeleitoral',
                'TIMEOUT': 7200,  # 2h
                'VERSION': 1,
            }
        }
        # Cache separado para sessões
        CACHES['sessions'] = {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': config('REDIS_URL'),
            'OPTIONS': CACHES['default']['OPTIONS'].copy(),
            'KEY_PREFIX': 'sessions',
            'TIMEOUT': 86400,  # 24h
        }
        SESSION_CACHE_ALIAS = 'sessions'
    except ImportError:
        pass  # Fallback para cache local
elif not DEBUG:
    # Otimizar cache local para produção sem Redis
    CACHES['default']['OPTIONS']['MAX_ENTRIES'] = 5000
    CACHES['default']['OPTIONS']['CULL_FREQUENCY'] = 4
    CACHES['default']['TIMEOUT'] = 7200

# === CONFIGURAÇÕES DE SESSÃO OTIMIZADAS ===
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
SESSION_SAVE_EVERY_REQUEST = False

# === CONFIGURAÇÕES DE ARQUIVOS ESTÁTICOS ===
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Configurações WhiteNoise otimizadas para performance
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG
WHITENOISE_MAX_AGE = 31536000  # 1 ano para arquivos estáticos
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'tgz', 'bz2', 'tbz', 'xz', 'br']

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# === CONFIGURAÇÕES DE SEGURANÇA ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Configurações de segurança específicas para Folium
SECURE_CONTENT_TYPE_NOSNIFF = False  # Necessário para iframes do Folium
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Permite iframes do mesmo domínio

# === CONFIGURAÇÕES DE LOCALIZAÇÃO ===
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# === CONFIGURAÇÕES DE LOGGING SIMPLIFICADAS ===
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
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'mapa_eleitoral': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# === CONFIGURAÇÕES ESPECÍFICAS PARA MAPA ELEITORAL ===
CACHE_TIMES = {
    'geojson_data': 86400,      # 24h
    'map_html': 43200,          # 12h
    'candidato_info': 21600,    # 6h
    'anos_eleicao': 86400,      # 24h
    'partidos': 21600,          # 6h
    'candidatos': 10800,        # 3h
    'votos_bairro': 7200,       # 2h
    'complete_data': 7200,      # 2h
}

# Reduzir tempos em desenvolvimento
if DEBUG:
    CACHE_TIMES = {k: min(v, 300) for k, v in CACHE_TIMES.items()}

# Configurações de performance para mapas
MAP_SETTINGS = {
    'max_zoom': 16,
    'min_zoom': 9,
    'default_zoom': 10,
    'choropleth_bins': 6,
    'smooth_factor': 1.0,
    'line_opacity': 0.3,
    'fill_opacity': 0.7,
    'coordinate_precision': 6,
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# === DEBUG TOOLBAR (APENAS EM DESENVOLVIMENTO) ===
if DEBUG:
    try:
        import debug_toolbar
        INSTALLED_APPS += ['debug_toolbar']
        MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
        INTERNAL_IPS = ['127.0.0.1', '::1']
        
        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
            'SHOW_COLLAPSED': True,
        }
    except ImportError:
        pass

# === CONFIGURAÇÕES DE PRODUÇÃO ===
if not DEBUG:
    # Configurações de segurança em produção
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000  # 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

# === FUNÇÃO DE SETUP DE DIRETÓRIOS ===
def setup_directories():
    """Cria diretórios necessários se não existirem"""
    directories = [
        os.path.join(BASE_DIR, 'logs'),
        os.path.join(BASE_DIR, 'static', 'maps'),
        os.path.join(STATIC_ROOT, 'maps') if STATIC_ROOT else None,
        MEDIA_ROOT,
    ]
    
    for directory in directories:
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except OSError:
                pass  # Ignorar erros de permissão

# Executar setup
setup_directories()

import logging

# ... (rest of the file)

# === VALIDAÇÃO DE CONFIGURAÇÕES ===
def validate_critical_settings():
    """Valida configurações críticas"""
    logger = logging.getLogger(__name__)
    errors = []
    
    # Verificar se arquivo GeoJSON existe
    geojson_path = os.path.join(BASE_DIR, 'mapa_eleitoral', 'data', 'Limite_Bairro.geojson')
    if not os.path.exists(geojson_path):
        errors.append(f"Arquivo GeoJSON não encontrado: {geojson_path}")
    
    # Verificar configurações de banco
    if not DATABASES['default']['NAME']:
        errors.append("Nome do banco de dados não configurado")
    
    if errors:
        for error in errors:
            logger.error(error)

# Executar validação
import sys
if 'runserver' in sys.argv or 'migrate' in sys.argv:
    validate_critical_settings()