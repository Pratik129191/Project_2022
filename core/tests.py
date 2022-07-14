import datetime
from django.contrib.auth import login
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect, render

from .models import User


def is_email_validated(email):
    try:
        validate_email(email)
    except ValidationError:
        return False
    else:
        return True


def get_username_of_this(email):
    user = User.objects.get(email=email)
    return user.username


def redirect_to_home_or_next_url(next_url):
    if next_url is not None:
        return redirect(next_url)
    else:
        return redirect('home')


def login_user_or_show_error_page(request, user):
    if user is not None:
        login(request, user)
        return redirect_to_home_or_next_url(request.GET.get('next'))
    else:
        return render(request, 'errors.html', {
            'errors': 'User ID or Password is Incorrect.',
            'name': 'Login'
        })


def calculate_age(birth_date):
    today = datetime.date.today()
    try:
        birthday = birth_date.replace(year=today.year)

    # raised when birth date is February 29
    # and the current year is not a leap year
    except ValueError:
        birthday = birth_date.replace(year=today.year,
                                      month=birth_date.month + 1, day=1)

    if birthday > today:
        age = today.year - birth_date.year - 1
        return str(age)
    else:
        age = today.year - birth_date.year
        return str(age)

