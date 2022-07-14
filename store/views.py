from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action

from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.renderers import AdminRenderer, JSONRenderer, TemplateHTMLRenderer

from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly

from .filters import TestFilter, QueryFilter, OrderFilter, ReviewFilter, DoctorFilter, ReportFilter
from .models import Test, OrderedTest, Doctor, Collection, Order, Checkup, Query, Review, TestImage, Report, Department
from .mixins import LoginRequiredMixin
from .pagination import DefaultPagination
from .permissions import IsAdminOrReadOnly
from .serializers import TestSerializer, DoctorSerializer, CollectionSerializer, OrderSerializer, \
    AddOrderedTestSerializer, CheckupSerializer, AddDoctorForCheckupSerializer, \
    AddQuerySerializer, QuerySerializer, ReviewSerializer, AddReviewSerializer, \
    TestImageSerializer, AddTestImageSerializer, ReportSerializer, DepartmentSerializer


class DepartmentViewSet(ModelViewSet):
    renderer_classes = [AdminRenderer]
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Department.objects.\
            annotate(doctors_count=Count('doctor')).\
            prefetch_related('doctor_set').all()

    def destroy(self, request, *args, **kwargs):
        if Doctor.objects.filter(department_id=kwargs['pk']).count() > 0:
            return Response({
                'error': 'This Collection can not be deleted as it has one or more Doctors.'
            })
        return super(DepartmentViewSet, self).destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    renderer_classes = [AdminRenderer]
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Collection.objects.\
            annotate(tests_count=Count('test')).\
            prefetch_related('test_set').all()

    def destroy(self, request, *args, **kwargs):
        if Test.objects.filter(collection_id=kwargs['pk']).count() > 0:
            return Response({
                'error': 'This collection can not be deleted, as it has 1 or more Tests.'
            })
        return super(CollectionViewSet, self).destroy(request, *args, **kwargs)


class TestViewSet(ModelViewSet):
    renderer_classes = [AdminRenderer]
    queryset = Test.objects.select_related('collection').prefetch_related('images').all()
    serializer_class = TestSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    pagination_class = DefaultPagination
    filterset_class = TestFilter
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price']
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        return {
            'request': self.request,
            'user_id': self.request.user.id
        }

    def destroy(self, request, *args, **kwargs):
        if OrderedTest.objects.filter(test_id=kwargs['pk']).count() > 0:
            return Response({
                'error': 'This test can not be deleted, as it has 1 or more orders.'
            })
        return super(TestViewSet, self).destroy(request, *args, **kwargs)


class DoctorViewSet(ModelViewSet):
    renderer_classes = [AdminRenderer]
    queryset = Doctor.objects.select_related('department', 'qualification').prefetch_related('timings').all()
    serializer_class = DoctorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = DoctorFilter
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        return {
            'request': self.request
        }

    @action(detail=True, renderer_classes=[TemplateHTMLRenderer])
    def schedule(self, request: HttpRequest, **kwargs):
        doctor = Doctor.objects.get(pk=kwargs['pk'])

        return render(
            request,
            'doctor_schedule.html',
            {
                'name': doctor.name(),
                'schedule': doctor.timings.all()
            }
        )


class OrderViewSet(LoginRequiredMixin, ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'put']
    renderer_classes = [AdminRenderer]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = OrderFilter
    ordering_fields = ['placed_at']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.select_related('user').\
                prefetch_related('tests__test').\
                filter(user_id=self.request.user.id).\
                order_by('-placed_at', '-payment_status')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddOrderedTestSerializer
        return OrderSerializer

    def get_serializer_context(self):
        return {
            'user_id': self.request.user.id,
            'user': self.request.user,
        }

    @action(detail=True, renderer_classes=[TemplateHTMLRenderer])
    def payment(self, request: HttpRequest, **kwargs):
        order = Order.objects.get(pk=kwargs['pk'])
        order.payment_status = order.PAYMENT_STATUS_COMPLETE
        order.save()
        total_payable = order.tests.unit_price
        return render(
            request,
            'order_payment_msg.html',
            {
                'value': total_payable,
                'id': kwargs['pk'],
                'order': reverse('store:orders-list')
            }
        )


class CheckupViewSet(LoginRequiredMixin, ModelViewSet):
    renderer_classes = [AdminRenderer]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['POST']:
            return AddDoctorForCheckupSerializer
        return CheckupSerializer

    def get_serializer_context(self):
        return {
            'user_id': self.request.user.id
        }

    def get_queryset(self):
        return Checkup.objects.select_related('user').\
            prefetch_related('doctors__doctor').\
            filter(user_id=self.request.user.id).\
            order_by('-booked_at', '-payment_status')

    @action(detail=True, renderer_classes=[JSONRenderer])
    def payment(self, request: HttpRequest, **kwargs):
        checkup = Checkup.objects.get(pk=kwargs['pk'])
        checkup.payment_status = checkup.PAYMENT_STATUS_COMPLETE
        checkup.save()
        total_payable = sum(item.doctor_fees for item in checkup.doctors.all())
        return render(
            request,
            'checkup_payment_msg.html',
            {
                'value': total_payable,
                'id': kwargs['pk'],
                'checkup': reverse('store:checkups-list')

            }
        )


class QueryViewSet(ModelViewSet):
    renderer_classes = [AdminRenderer]
    http_method_names = ['get', 'post', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = QueryFilter
    queryset = Query.objects.all().order_by('-date')
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddQuerySerializer
        return QuerySerializer


class ReviewViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReviewFilter
    renderer_classes = [AdminRenderer]
    queryset = Review.objects.select_related('user', 'test').all().order_by('-date')
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        return {
            'user_id': self.request.user.id
        }

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddReviewSerializer
        return ReviewSerializer


class TestImageViewSet(LoginRequiredMixin, ModelViewSet):
    renderer_classes = [AdminRenderer]
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TestImageSerializer
        return AddTestImageSerializer

    def get_serializer_context(self):
        return {
            'test_id': self.kwargs['test_pk'],
        }

    def get_queryset(self):
        return TestImage.objects.filter(test_id=self.kwargs['test_pk'])


class ReportViewSet(LoginRequiredMixin, ModelViewSet):
    renderer_classes = [AdminRenderer]
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = ReportSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReportFilter

    def get_queryset(self):
        return Report.objects.filter(user_id=self.request.user.id).order_by('-date')

