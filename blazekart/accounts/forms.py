from django import forms
from .models import Account
import re
class RegistrationForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control password-field','placeholder':'Enter your Password...',}))

    confirm_password=forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control password-field','placeholder':'Re-Enter your Password...'}))

    class Meta:
        model=Account
        fields=['first_name','last_name','phone_no','email','password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        # Password match check (NON-FIELD error)
        if password and confirm_password and password != confirm_password:
            self.add_error( None,"Please make sure both passwords are the same.")

        return cleaned_data


    def clean_phone_no(self):
        phone_no = self.cleaned_data.get("phone_no")

        if phone_no and not re.fullmatch(r"\d+", phone_no):
            raise forms.ValidationError("Phone number must contain only digits.")

        return phone_no

