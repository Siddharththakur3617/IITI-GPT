from pathlib import Path

BASE_DIR = Path(__file__).parent
SECRET_KEY = "dev-only-change-me"
DEBUG = True
ALLOWED_HOSTS = []
ROOT_URLCONF = "urls"

INSTALLED_APPS = ["django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions"]
MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
    ]},
}]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "chat"
LOGOUT_REDIRECT_URL = "login"
