from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class MinimumLengthValidator:
    """Validate that the password has at least 8 characters."""
    
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("Password must be at least %(min_length)d characters long"),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return _("Your password must contain at least %(min_length)d characters.") % {
            'min_length': self.min_length
        }


class CommonPasswordValidator:
    """Validate that the password is not too simple or commonly used."""
    
    COMMON_PASSWORDS = {
        'password', 'password1', 'password123', '123456', '12345678',
        'qwerty', 'abc123', 'monkey', 'letmein', 'dragon', 'master',
        'admin', 'welcome', 'login', 'princess', 'sunshine', 'shadow',
    }

    def validate(self, password, user=None):
        if password.lower() in self.COMMON_PASSWORDS:
            raise ValidationError(
                _("Please choose a more unique password — this one is too easy to guess"),
                code='password_too_common',
            )

    def get_help_text(self):
        return _("Your password should not be a commonly used password.")


class NumericPasswordValidator:
    """Validate that the password is not entirely numeric."""

    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                _("Password cannot be only numbers — please include some letters"),
                code='password_entirely_numeric',
            )

    def get_help_text(self):
        return _("Your password should not be entirely numeric.")


class UserAttributeSimilarityValidator:
    """Validate that the password is not too similar to user attributes."""
    
    def __init__(self, user_attributes=('username', 'email', 'first_name', 'last_name'), max_similarity=0.7):
        self.user_attributes = user_attributes
        self.max_similarity = max_similarity

    def validate(self, password, user=None):
        if not user:
            return

        for attribute_name in self.user_attributes:
            value = getattr(user, attribute_name, None)
            if not value or not isinstance(value, str):
                continue
            
            value_lower = value.lower()
            password_lower = password.lower()
            
            if value_lower in password_lower or password_lower in value_lower:
                raise ValidationError(
                    _("Password is too similar to your %(attribute)s — please choose something different"),
                    code='password_too_similar',
                    params={'attribute': attribute_name.replace('_', ' ')},
                )

    def get_help_text(self):
        return _("Your password should not be too similar to your personal information.")
