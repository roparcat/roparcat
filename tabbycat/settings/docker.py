# ==============================================================================
# Docker
# ==============================================================================

import os

ALLOWED_HOSTS = ["*"]

# docker-compose.yml refuses to start without SECRET_KEY in .env; the
# fallback to core.py's public key only covers collectstatic at build time
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)  # noqa: F821 (from core.py)

# nginx forwards the original scheme (see config/nginx.conf)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tabbycat',
        'USER': 'tabbycat',
        'PASSWORD': 'tabbycat',
        'HOST': 'db',
        'PORT': 5432, # Non-standard to prevent collisions,
    }
}

if bool(int(os.environ['DOCKER_REDIS'])) if 'DOCKER_REDIS' in os.environ else False:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://redis:6379/1",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "SOCKET_CONNECT_TIMEOUT": 5,
                "SOCKET_TIMEOUT": 60,
            },
        },
    }

    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [("redis", 6379)],
                "group_expiry": 10800,
            },
        },
    }

# Email over SMTP, configured in .env (see CLAUDE.md); without EMAIL_HOST no
# email is sent
if os.environ.get('EMAIL_HOST', ''):
    SERVER_EMAIL = os.environ['DEFAULT_FROM_EMAIL']
    DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']
    EMAIL_HOST = os.environ['EMAIL_HOST']
    EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'true').lower() == 'true'
