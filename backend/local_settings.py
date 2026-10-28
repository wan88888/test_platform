"""Single-process local demo. Production continues to use backend.settings."""
from backend.settings import *  # noqa: F401,F403

LOCAL_DIR = BASE_DIR / '.local'
LOCAL_DIR.mkdir(exist_ok=True)
SECRET_FILE = LOCAL_DIR / 'secret-key'
if not SECRET_FILE.exists():
    from django.core.management.utils import get_random_secret_key
    SECRET_FILE.write_text(get_random_secret_key())
    SECRET_FILE.chmod(0o600)
SECRET_KEY = SECRET_FILE.read_text().strip()
SIMPLE_JWT = {**SIMPLE_JWT, 'SIGNING_KEY': SECRET_KEY}

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': LOCAL_DIR / 'testhub.sqlite3',
        'OPTIONS': {'timeout': 30},
    }
}
CHANNEL_LAYERS = {'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'}}
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:3001', 'http://localhost:3001']
CORS_ALLOWED_ORIGINS = CSRF_TRUSTED_ORIGINS
APP_USE_HTTPS = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_PROXY_SSL_HEADER = None
SIMPLEUI_INDEX = 'http://127.0.0.1:3001'
