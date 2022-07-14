from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from rest_framework.renderers import AdminRenderer
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from twilio.rest import Client


from .permissions import IsAdminOrReadOnly, IsAuthenticatedOrReadOnly
from .forms import UserCreationForm
from .models import User
from .serializers import UserProfileSerializer
from .tests import is_email_validated, get_username_of_this, login_user_or_show_error_page


def register_user(request):
    form = UserCreationForm()
    context = {
        'form': form,
        'login': reverse('core:login')
    }
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account is Successfully Created for ' + form.cleaned_data.get('username'))
            return redirect('core:login')
        else:
            return render(request, 'errors.html', {
                'errors': form.errors,
                'name': 'Registration'

            })
    return render(
        request,
        'register.html',
        context=context
    )


def login_user(request):
    context = {
        'register': reverse('core:register'),
        'forgot_password': reverse('core:forgot_password')
    }

    if request.method == 'POST':
        user_name_or_email = request.POST.get('username')
        password = request.POST.get('password')
        if is_email_validated(user_name_or_email):
            username = get_username_of_this(user_name_or_email)
            user = authenticate(request, username=username, password=password)
            return login_user_or_show_error_page(request, user)
        else:
            username = user_name_or_email
            user = authenticate(request, username=username, password=password)
            return login_user_or_show_error_page(request, user)
    return render(request, 'login.html', context=context)


def logout_user(request):
    logout(request)
    return redirect('core:login')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        birth_date = request.POST.get('birth_date')
        try:
            user = User.objects.get(email=email, birth_date=birth_date)
            return render(
                request,
                'show_password.html',
                {
                    'register': reverse('core:register'),
                    'username': user.username,
                    'password': user.password_store
                }
            )
        except User.DoesNotExist:
            return render(
                request,
                'errors.html',
                {
                    'errors': "Looks You Haven't Registered Yet!",
                    'name': 'Resetting',
                    'register': reverse('core:register')
                }
            )
    return render(
        request,
        'forgot_password.html',
        {
            'register': reverse('core:register')
        }
    )


class UserProfileViewSet(RetrieveModelMixin,
                         UpdateModelMixin,
                         ListModelMixin,
                         GenericViewSet):
    renderer_classes = [AdminRenderer]
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.id)


