from django.core.validators import MinLengthValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.html import format_html


class User(AbstractUser):
    SEX_MALE = 'M'
    SEX_FEMALE = 'F'
    SEX_TRANS = 'T'
    SEX_CHOICE = [
        (SEX_MALE, 'Male'),
        (SEX_FEMALE, 'Female'),
        (SEX_TRANS, 'Trans Gender')
    ]

    first_name = models.CharField(max_length=150, null=True)
    last_name = models.CharField(max_length=150, null=True)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=300, null=True)
    password_store = models.CharField(max_length=250, null=True)
    phone = models.CharField(
        max_length=10,
        null = True,
        validators=[
            MinLengthValidator(10)
        ]
    )
    sex = models.CharField(max_length=1, choices=SEX_CHOICE, null=True)
    age = models.CharField(max_length=5, null=True)
    birth_date = models.DateField(null=True)
    doctor_name = models.CharField(
        max_length=255,
        help_text='Name of the Doctor Referred You. If not please Ignore.',
        default='self',
        blank=True,
        null=True
    )

    def name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        url = reverse('core:logout')
        log_out = format_html('<a href={}>Logout</a>', url)
        return f"{self.first_name} {self.last_name}"


