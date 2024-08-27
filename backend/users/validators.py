from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from recipes.constants import RESTRICTED_USERNAME, USERNAME_REGEX


def validate_username(value):
    if value == RESTRICTED_USERNAME:
        raise ValidationError(f'Username cannot be "{RESTRICTED_USERNAME}".')


username_validator = RegexValidator(
    regex=USERNAME_REGEX,
    message='Username must be alphanumeric'
            'or contain any of the following: @/./+/-/_'
)
