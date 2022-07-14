from django_filters.rest_framework import FilterSet
from . import models


class TestFilter(FilterSet):
    class Meta:
        model = models.Test
        fields = {
            'collection_id': ['exact'],
            'unit_price': ['gt', 'lt'],
        }


class QueryFilter(FilterSet):
    class Meta:
        model = models.Query
        fields = {
            'id': ['exact'],
            'name': ['icontains'],
        }


class OrderFilter(FilterSet):
    class Meta:
        model = models.Order
        fields = {
            'payment_status': ['exact'],
        }


class ReviewFilter(FilterSet):
    class Meta:
        model = models.Review
        fields = {
            'test': ['exact']
        }


class DoctorFilter(FilterSet):
    class Meta:
        model = models.Doctor
        fields = {
            'department': ['exact'],
            'qualification': ['exact'],
        }


class ReportFilter(FilterSet):
    class Meta:
        model = models.Report
        fields = {
            'test': ['exact'],
        }


class OrderedTestFilter(FilterSet):
    class Meta:
        model = models.OrderedTest
        fields = {
            'test': ['exact']
        }

