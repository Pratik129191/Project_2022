import time
from datetime import datetime

from django.contrib import admin
from django.db import models
from django.core.validators import MinValueValidator, MinLengthValidator
from django.conf import settings


class Department(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title


class Qualification(models.Model):
    name = models.CharField(max_length=300, unique=True)
    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.title} [ {self.name} ]"


class Doctor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=10,
        validators=[
            MinLengthValidator(10)
        ]
    )
    qualification = models.ForeignKey(Qualification, on_delete=models.PROTECT)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    fees = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[
            MinValueValidator(1),
        ]
    )
    last_update = models.DateTimeField(auto_now=True)
    address = models.TextField()
    image = models.ImageField(
        upload_to='store/images',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['first_name', 'last_name']


class Day(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Timing(models.Model):
    start = models.TimeField()
    end = models.TimeField()
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='timings')

    def convert_to_12_hour(self, value, formating_24="%H:%M:%S"):
        formating_12 = "%I:%M %p"
        value = str(value)
        time24 = datetime.strptime(value, formating_24)
        time12 = time24.strftime(formating_12)
        return time12

    def __str__(self):
        return f"{self.convert_to_12_hour(self.start)} to {self.convert_to_12_hour(self.end)}"


class Collection(models.Model):
    title = models.CharField(max_length=255, unique=True)
    featured_test = models.ForeignKey(
        'Test',
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
        blank=True
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class Test(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    code = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[
            MinValueValidator(1),
        ]
    )
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.title} [{self.code}]"

    class Meta:
        ordering = ['title']


class TestImage(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='store/images')


class Checkup(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICE = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed')
    ]

    booked_at = models.DateField(auto_now=True)
    payment_status = models.CharField(
        max_length=1,
        choices=PAYMENT_STATUS_CHOICE,
        default=PAYMENT_STATUS_PENDING
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)


class DoctorForCheckup(models.Model):
    checkup = models.ForeignKey(Checkup, on_delete=models.PROTECT, related_name='doctors')
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT)
    doctor_fees = models.DecimalField(
        max_digits=6,
        decimal_places=0,
        validators=[
            MinValueValidator(1),
        ]
    )


class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICE = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed')
    ]

    placed_at = models.DateField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1,
        choices=PAYMENT_STATUS_CHOICE,
        default=PAYMENT_STATUS_PENDING
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self):
        return f"Order ID {self.id}"

    class Meta:
        permissions = [
            ('cancel_order', 'Can Cancel Order')
        ]


class OrderedTest(models.Model):
    DEFAULT_QUANTITY = 1

    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name='tests')
    test = models.ForeignKey(Test, on_delete=models.PROTECT)
    quantity = models.IntegerField(
        default=DEFAULT_QUANTITY,
        validators=[
            MinValueValidator(1),
        ]
    )
    unit_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[
            MinValueValidator(1),
        ]
    )

    def __str__(self):
        return self.test.title


class Review(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)


class Query(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(
        max_length=10,
        validators=[
            MinLengthValidator(10)
        ]
    )
    date = models.DateField(auto_now_add=True)
    question = models.TextField()
    answer = models.TextField(null=True, blank=True)


class Subscribe(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.email}"


class Report(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='reports')
    test = models.ForeignKey(Test, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    detail = models.TextField()
    date = models.DateField(auto_now_add=True)
