from django.contrib.auth.mixins import LoginRequiredMixin as BaseLoginRequiredMixin
from django.urls import reverse


class LoginRequiredMixin(BaseLoginRequiredMixin):
    def get_login_url(self):
        return str(reverse('core:login'))

