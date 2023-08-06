"""Configuration for the dj_core_drf app."""
from datetime import timedelta

from dj_core.config import Config as BaseConfig, DefaultProxy


class Config(BaseConfig):
    """Override config to inject our defaults."""

    defaults = BaseConfig.defaults.copy()
    defaults.update({
        'ACCOUNT_AUTHENTICATION_METHOD': 'email',
        'ACCOUNT_EMAIL_REQUIRED': True,
        'ACCOUNT_EMAIL_VERIFICATION': 'none',
        'ACCOUNT_USER_MODEL_USERNAME_FIELD': None,
        'ACCOUNT_USERNAME_REQUIRED': False,
        'ACCOUNT_REGISTRATION': 'enabled',
        'REST_USE_JWT': True,
        'SWAGGER_SETTINGS': {'api_version': '1'},
        'JWT_AUTH': {
            'JWT_EXPIRATION_DELTA': timedelta(hours=24),
            'JWT_AUTH_HEADER_PREFIX': 'Token',
        },
        'REST_FRAMEWORK': DefaultProxy({}, 'get_drf_settings'),
        'REST_AUTH_SERIALIZERS': DefaultProxy({}, 'get_rest_auth_serializers'),
        'REST_AUTH_REGISTER_SERIALIZERS':
            DefaultProxy({}, 'get_rest_auth_register_serializers'),
    })
    defaults.INSTALLED_APPS_REQUIRED = [
        'dj_core_drf',
        'rest_framework',
        'rest_framework.authtoken',
        'rest_framework_swagger',
        'rest_auth',
        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        'rest_auth.registration',
        'django_filters',
    ] + defaults.INSTALLED_APPS_REQUIRED
    defaults.INSTALLED_APPS_OPTIONAL += [
        'revproxy',
    ]

    # pylint: disable=unused-argument,no-self-use
    def get_drf_settings(self, settings):
        """Return a default settings dict for DRF."""
        return {
            'DEFAULT_PERMISSION_CLASSES': [
                'rest_framework.permissions.IsAuthenticatedOrReadOnly'
            ],
            'DEFAULT_AUTHENTICATION_CLASSES': [
                'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
                'rest_framework.authentication.BasicAuthentication',
                'rest_framework.authentication.SessionAuthentication',
            ],
            'DEFAULT_PAGINATION_CLASS':
                'dj_core_drf.pagination.ThousandMaxLimitOffsetPagination',
            'DEFAULT_FILTER_BACKENDS': [
                'rest_framework_filters.backends.DjangoFilterBackend',
            ],
            'DEFAULT_METADATA_CLASS':
                'dj_core_drf.metadata.ModelChoicesMetadata',
        }

    # pylint: disable=unused-argument,no-self-use
    def get_rest_auth_serializers(self, settings):
        """Return a default settings dict for rest_auth."""
        return {
            'USER_DETAILS_SERIALIZER':
                'dj_core_drf.serializers.UserDetailsSerializer',
            'PASSWORD_RESET_SERIALIZER':
                'dj_core_drf.serializers.PasswordResetSerializer',
            'LOGIN_SERIALIZER': 'dj_core_drf.serializers.LoginSerializer',
        }

    # pylint: disable=unused-argument,no-self-use
    def get_rest_auth_register_serializers(self, settings):
        """Return a default settings dict for rest_auth.registration."""
        return {
            'REGISTER_SERIALIZER':
                'dj_core_drf.serializers.RegisterSerializer',
        }
