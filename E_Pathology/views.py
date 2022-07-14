from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.admin.sites import site
from store.models import Subscribe


def home_page(request):
    url = (
            reverse('core:profile-list')
            + str(request.user.id)
    )

    return render(
        request,
        'home_page.html',
        {
            'user': request.user.username,
            'profile': url,
            'home': reverse('home'),
            'subscribe': reverse('subscribe'),
            'user_login': reverse('core:login'),
            'admin_login': reverse('admin:login'),
            'logout': reverse('core:logout'),
            'register': reverse('core:register'),
            'collections': reverse('store:collections-list'),
            'departments': reverse('store:departments-list'),
            'tests': reverse('store:tests-list'),
            'doctors': reverse('store:doctors-list'),
            'orders': reverse('store:orders-list'),
            'checkups': reverse('store:checkups-list'),
            'querys': reverse('store:querys-list'),
            'reviews': reverse('store:reviews-list'),
            'reports': reverse('store:reports-list')
        }
    )


def subscription_page(request):
    context = {}
    if request.method == 'POST':
        input_name = request.POST.get('name')
        input_email = request.POST.get('email')
        if input_name or input_email == '':
            return render(
                request,
                'errors.html',
                {
                    'errors': 'Please Fill out Your Name & Email.',
                    'name': 'Blank Subscription',
                    'subscribe': reverse('subscribe')
                }
            )
        queryset = Subscribe.objects.values('email')
        emails_list = []
        for dictn in queryset:
            emails_list.append(dictn['email'])

        if input_email not in emails_list:
            Subscribe.objects.create(
                name=input_name,
                email=input_email
            )
            return redirect('home')
        else:
            return render(
                request,
                'errors.html',
                {
                    'errors': 'You are already Subscribed.',
                    'name': 'Subscription',
                    'home': reverse('home')
                }
            )

    return render(request, 'subscribe.html', context=context)
