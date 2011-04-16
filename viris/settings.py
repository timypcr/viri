import os
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
TEMPLATE_DEBUG = False
ADMINS = MANAGERS = (
    ('Viri Admin', 'admin@viriproject.com'),
)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_PATH, 'viris.sqlite'),
    }
}
TIME_ZONE = 'America/Los_Angeles'
LANGUAGE_CODE = 'en-us'
USE_I18N = False
USE_L10N = False
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(PROJECT_PATH, 'media', 'static')
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/media/admin/'
STATICFILES_DIRS = []
STATICFILES_FINDERS = []
SECRET_KEY = '^#vk$dcljhj%t(xc#f)skfhss(rpx%=fb3sfht6g)*hmh^fn*t'
TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)
ROOT_URLCONF = 'urls'
TEMPLATE_DIRS = []
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'hosts',
    'firewall',
    'cron',
)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
HOST_INLINES = ('firewall.admin.HostRuleAdmin',)
