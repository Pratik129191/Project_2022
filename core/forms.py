from datetime import date
from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm

from .models import User
from .tests import calculate_age


class DateInput(forms.DateInput):
    input_type = 'date'


class UserCreationForm(BaseUserCreationForm):
    birth_date = forms.DateField(widget=DateInput(format='%y-%m-%d'))
    address = forms.CharField(widget=forms.TextInput(attrs={'size': 80}))

    def save(self, commit=True):
        self.instance = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password2'],
            password_store=self.cleaned_data['password2'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
            phone=self.cleaned_data['phone'],
            birth_date=self.cleaned_data['birth_date'],
            sex=self.cleaned_data['sex'],
            age=self.cleaned_data['age'],
            address=self.cleaned_data['address'],
            doctor_name=self.cleaned_data['doctor_name'],
        )
        return self.instance

    class Meta(BaseUserCreationForm.Meta):
        model = User
        fields = [
            'username', 'password1', 'password2',
            'first_name', 'last_name', 'email',
            'phone', 'birth_date', 'sex', 'age',
            'address', 'doctor_name'
        ]

        widgets = {
            'sex': forms.Select(attrs={'style': 'width:540px; height: 35px'})
        }
