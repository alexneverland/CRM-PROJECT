# crm_project/settings.py

from pathlib import Path
import os # Προστέθηκε για το os.path.join αν δεν χρησιμοποιείς Path για templates DIRS
from dotenv import load_dotenv

load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY') # <<< ΑΛΛΑΞΕ ΤΟ ΑΥΤΟ!

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core.apps.CoreConfig', # Η εφαρμογή σου (ή απλά 'core')
]

MIDDLEWARE = [
    
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'crum.CurrentRequestUserMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'crm_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # <<< ΕΔΩ ΕΙΝΑΙ Η ΡΥΘΜΙΣΗ ΓΙΑ ΤΟΝ project-level templates FOLDER
        # Εναλλακτικά, αν προτιμάς το os.path.join:
        # 'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.theme_colors_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'crm_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {    
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'crm_db_lazaros',        # Το όνομα της βάσης που δημιούργησες
        'USER': 'neverland',     # Ο χρήστης που δημιούργησες
        'PASSWORD': '2710', # Ο κωδικός του χρήστη
        'HOST': 'localhost',            # Συνήθως 'localhost' αν ο PostgreSQL server είναι στο ίδιο μηχάνημα
        'PORT': '5432',  
    }
}
#DATABASES = {
    #'default': {
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': BASE_DIR / 'db.sqlite3',
    #}
#}
COMPANY_INFO = {
    'NAME': 'lazaros_solutions',
    'ADDRESS': 'Πιστων 7, Θεσσαλονικη 54632',
    'PHONE': '6973828408',
    'EMAIL': 'neverlandxx@gmail.com',
    'VAT_NUMBER': '1235678',
    'DOY': 'Ε θεσσαλονικης',
    # Μπορείς να προσθέσεις κι άλλα αν χρειάζεται, π.χ., website, λογότυπο (ως URL)
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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'el' # <<< ΡΥΘΜΙΣΗ ΓΙΑ ΕΛΛΗΝΙΚΑ

TIME_ZONE = 'Europe/Athens' # <<< ΡΥΘΜΙΣΗ ΓΙΑ ΖΩΝΗ ΩΡΑΣ ΕΛΛΑΔΑΣ

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
# STATICFILES_DIRS = [BASE_DIR / 'static'] # Αν έχεις έναν project-level static φάκελο

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Email Configuration (for development - prints emails to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Ρυθμίσεις Αυθεντικοποίησης
LOGIN_REDIRECT_URL = 'home'        # Όνομα URL για ανακατεύθυνση μετά το login
LOGOUT_REDIRECT_URL = 'home'       # Όνομα URL για ανακατεύθυνση μετά το logout
LOGIN_URL = '/accounts/login/'     # Το URL της σελίδας εισόδου

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')