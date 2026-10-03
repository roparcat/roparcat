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
