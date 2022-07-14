from django.urls import reverse
from django.utils.html import format_html
from rest_framework import serializers
from .models import User


class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    sex = serializers.SerializerMethodField()

    def get_sex(self, user: User):
        if user.sex == User.SEX_MALE:
            return 'Male'
        elif user.sex == User.SEX_FEMALE:
            return 'Female'
        else:
            return 'Transgender'

    def get_id(self, user: User):
        url = (
                reverse('core:profile-list')
                + str(user.id)
        )
        return format_html('<a href={}>📌({})</a>', url, user.id)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'address',
                  'phone', 'sex', 'age', 'birth_date',
                  'doctor_name']




