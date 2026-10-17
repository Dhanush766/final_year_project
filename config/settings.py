"""
Django settings for the Employee Management System.

All secrets and environment-specific values (secret key, database
credentials, debug flag, allowed hosts) are read from environment
variables. For local development they are loaded from a `.env` file
(copy `.env.example` to `.env`). The `.env` file is ignored by Git.
"""
import os
from pathlib import Path

from django.contrib.messages import constants as message_constants
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load variables from .env (if the file exists). Real environment
# variables always take priority over values in the file.
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    """Read a True/False value from an environment variable."""
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def require_env(name):
    """Return an environment variable or stop with a clear error message."""
    value = os.getenv(name)
    if value is None or value == "":
        raise ImproperlyConfigured(
            f"Environment variable {name} is not set. "
            "Copy .env.example to .env and fill in the values."
        )
    return value


# ---------------------------------------------------------------------------
# Core security settings
# ---------------------------------------------------------------------------
SECRET_KEY = require_env("DJANGO_SECRET_KEY")
DEBUG = env_bool("DJANGO_DEBUG", False)
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

# Extra protection that should be switched on when the site is served over
# HTTPS in production (set USE_HTTPS=True in the environment).
USE_HTTPS = env_bool("USE_HTTPS", False)
if USE_HTTPS:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 3600  # raise gradually once HTTPS works correctly

# ---------------------------------------------------------------------------
# Applications and middleware
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "employees.apps.EmployeesConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "employees.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Database (MySQL by default; SQLite is available for quick local testing)
# ---------------------------------------------------------------------------
DB_ENGINE = os.getenv("DB_ENGINE", "mysql").strip().lower()

if DB_ENGINE == "mysql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": require_env("DB_NAME"),
            "USER": require_env("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("DB_PORT", "3306"),
            "OPTIONS": {"charset": "utf8mb4"},
            "TEST": {
                "CHARSET": "utf8mb4",
                "COLLATION": "utf8mb4_unicode_ci",
            },
        }
    }
elif DB_ENGINE == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / os.getenv("SQLITE_NAME", "db.sqlite3"),
        }
    }
else:
    raise ImproperlyConfigured("DB_ENGINE must be either 'mysql' or 'sqlite'.")

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "employees:dashboard"
LOGOUT_REDIRECT_URL = "login"

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # used by `collectstatic` in production

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Messages: map Django's "error" level to Bootstrap's "danger" alert colour
# ---------------------------------------------------------------------------
MESSAGE_TAGS = {message_constants.ERROR: "danger"}

# ---------------------------------------------------------------------------
# Application-specific settings
# ---------------------------------------------------------------------------
SITE_NAME = "Employee Management System"
CURRENCY_SYMBOL = os.getenv("CURRENCY_SYMBOL", "₹")  # default: Indian rupee

# ---------------------------------------------------------------------------
# Logging (errors and warnings are printed to the console)
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[{levelname}] {asctime} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        "employees": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
