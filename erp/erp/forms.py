from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomPasswordResetForm(PasswordResetForm):
    username = forms.CharField(max_length=150, required=True)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        try:
            user = User.objects.get(username=username, email=email)
            if not user.is_superuser:
                raise forms.ValidationError("Password reset is only available for admin users.")
        except User.DoesNotExist:
            raise forms.ValidationError("Invalid username or email address.")

        return cleaned_data 