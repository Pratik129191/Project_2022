import datetime
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from rest_framework import serializers

from . import models
from .models import Order, OrderedTest, Checkup, DoctorForCheckup, TestImage


class DepartmentSerializer(serializers.ModelSerializer):
    doctors_count = serializers.SerializerMethodField()

    def get_doctors_count(self, department: models.Department):
        url = (
                reverse('store:doctors-list')
                + '?'
                + urlencode({
                    'department': str(department.id)
                })
        )
        return format_html('<a href={}>{} Doctors</a>', url, department.doctor_set.count())

    class Meta:
        model = models.Department
        fields = ['id', 'title', 'doctors_count']


class CollectionSerializer(serializers.ModelSerializer):
    tests_count = serializers.SerializerMethodField()

    def get_tests_count(self, collection: models.Collection):
        url = (
                reverse('store:tests-list')
                + '?'
                + urlencode({
                    'collection_id': str(collection.id)
                })
        )
        return format_html('<a href={}>{} Tests</a>', url, collection.test_set.count())

    class Meta:
        model = models.Collection
        fields = ['id', 'title', 'tests_count']


class AddTestImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        test_id = self.context['test_id']
        return TestImage.objects.create(test_id=test_id, **validated_data)

    class Meta:
        model = models.TestImage
        fields = ['image']


class TestImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, test_image: models.TestImage):
        return format_html(
            f"<a href='{test_image.image.url}'>"
            f"<img src='{test_image.image.url}' style='object-fit: cover; width: 100px; height: 100px;' />"
            f"</a>"
        )

    class Meta:
        model = models.TestImage
        fields = ['image']


class TestSerializer(serializers.ModelSerializer):
    # images = TestImageSerializer(many=True, read_only=True)
    title = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()
    collection = serializers.SerializerMethodField()

    # images = serializers.SerializerMethodField()

    # def get_images(self, test: models.Test):
    #     queryset = test.images.filter(test_id=test.id)
    #     html_image_list = []
    #     for item in queryset:
    #         html_img = format_html(
    #             f"<img src='{item.image.url}' style='object-fit: cover; width: 100px; height: 100px;' />"
    #         )
    #         html_image_list.append(html_img)
    #         # html_image_list.append(format_html('<br><br>'))
    #     return html_image_list

    def get_title(self, test: models.Test):
        url = (
                reverse('store:tests-list')
                + str(test.id)
        )
        return format_html('<a href={}>{}</a>', url, test.title)

    def get_reviews(self, test: models.Test):
        url = (
                reverse('store:reviews-list')
                + '?'
                + urlencode({
                    'test': str(test.id)
                })
        )
        return format_html('<a href="{}">See Reviews!</a>', url)

    def get_order(self, test: models.Test):
        url = (
            reverse('store:orders-list')
        )
        return format_html('<a href="{}">⚡Place Order!</a>', url)

    def get_collection(self, test: models.Test):
        return test.collection.title

    class Meta:
        model = models.Test
        fields = [
            'title', 'code',
            'unit_price', 'collection',
            'reviews', 'order',
        ]


class SimpleTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Test
        fields = ['id', 'title']


class DoctorSerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField()
    qualification = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    checkup = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_qualification(self, doctor: models.Doctor):
        return doctor.qualification.title

    def get_department(self, doctor: models.Doctor):
        return doctor.department.title

    def get_image(self, doctor: models.Doctor):
        if doctor.image.name != '':
            return format_html(
                f"<a href='{doctor.image.url}'>"
                f"<img src='{doctor.image.url}' "
                f"style='object-fit: cover; width: 125px; height: 125px;' "
                f"/>"
                f"</a>"
            )
        else:
            return ''

    def get_name(self, docotor: models.Doctor):
        url = (
                reverse('store:doctors-list')
                + str(docotor.id)
        )
        return format_html('<a href={}>{}</a>', url, docotor.name())

    def get_checkup(self, doctor: models.Doctor):
        url = (
            reverse('store:checkups-list')
        )
        return format_html('<a href="{}">⚡Book Checkup!</a>', url)

    def get_availability(self, doctor: models.Doctor):
        url = (
                reverse('store:doctors-list')
                + str(doctor.id)
                + str('/schedule/')
        )
        return format_html('<a href="{}">See Schedule</a>', url)

    class Meta:
        model = models.Doctor
        fields = ['name', 'qualification', 'department', 'availability', 'fees', 'checkup', 'image']


class SimpleDoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Doctor
        fields = ['id', 'name', 'fees']


class AddOrderedTestSerializer(serializers.ModelSerializer):
    def save(self, **kwargs):
        user_id = self.context['user_id']
        test = self.validated_data['test']
        quantity = OrderedTest.DEFAULT_QUANTITY

        # here one 'order' object will be created for every tests for the user.
        order = Order.objects.create(user_id=user_id)
        self.instance = OrderedTest.objects.create(
            order=order,
            test=test,
            quantity=quantity,
            unit_price=test.unit_price
        )
        return self.instance

    class Meta:
        model = models.OrderedTest
        fields = ['test']


class OrderedTestSerializer(serializers.ModelSerializer):
    test = SimpleTestSerializer()

    class Meta:
        model = models.OrderedTest
        fields = ['id', 'test']


class OrderSerializer(serializers.ModelSerializer):
    tests = OrderedTestSerializer()
    payment_status = serializers.SerializerMethodField()
    total_payable = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    reports = serializers.SerializerMethodField()

    def get_reports(self, order: models.Order):
        try:
            report = models.Report.objects.get(order_id=order.id)
            url = (
                    reverse('store:reports-list')
                    + str(report.id)
            )
            return format_html('<a href="{}" style="color: GREEN">View Report!</a>', url)
        except models.Report.DoesNotExist:
            return format_html('<h5 style="color: RED">Pending!</h5>')

    def get_id(self, order: models.Order):
        url = (
                reverse('store:orders-list')
                + str(order.id)
        )
        return format_html('<a href={}>📌({})</a>', url, order.id)

    def get_payment_status(self, order: models.Order):
        if order.payment_status == order.PAYMENT_STATUS_PENDING:
            url = (
                    reverse('store:orders-list')
                    + str(order.id)
                    + str('/payment/')
            )
            return format_html('<a href={}>👉Click to Pay!👈</a>', url)
        elif order.payment_status == order.PAYMENT_STATUS_COMPLETE:
            return format_html('<h5 style="color: GREEN">Payment Successfull</h5>')
        else:
            url = (
                    reverse('store:orders-list')
                    + str(order.id)
                    + str('/payment/')
            )
            pay = format_html('<a href={}>👉Click Again to Pay!👈</a>', url)
            return format_html('<h5 style="color: RED">Payment Failed</h5><p>{}</p>', pay)

    def get_total_payable(self, order: models.Order):
        return order.tests.unit_price
        # return sum([item.unit_price * item.quantity for item in order.tests.all()])

    class Meta:
        model = models.Order
        fields = ['id', 'placed_at', 'tests', 'total_payable', 'reports', 'payment_status']


class AddDoctorForCheckupSerializer(serializers.ModelSerializer):
    def save(self, **kwargs):
        user_id = self.context['user_id']
        doctor = self.validated_data['doctor']

        try:
            checkup = Checkup.objects.get(
                user_id=user_id,
                booked_at=datetime.date.today(),
                payment_status=Checkup.PAYMENT_STATUS_PENDING
            )
            try:
                self.instance = DoctorForCheckup.objects.get(checkup=checkup, doctor=doctor)
                return self.instance
            except DoctorForCheckup.DoesNotExist:
                self.instance = DoctorForCheckup.objects.create(
                    checkup=checkup,
                    doctor=doctor,
                    doctor_fees=doctor.fees
                )
                return self.instance
        except Checkup.DoesNotExist:
            checkup = Checkup.objects.create(user_id=user_id)
            self.instance = DoctorForCheckup.objects.create(
                checkup=checkup,
                doctor=doctor,
                doctor_fees=doctor.fees
            )
            return self.instance

    class Meta:
        model = models.DoctorForCheckup
        fields = ['id', 'doctor']


class DoctorForCheckupSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    visiting_charge = serializers.SerializerMethodField()

    def get_name(self, doctor_for_checkup: models.DoctorForCheckup):
        return doctor_for_checkup.doctor.name()

    def get_visiting_charge(self, doctor_for_checkup: models.DoctorForCheckup):
        return doctor_for_checkup.doctor_fees

    class Meta:
        model = models.DoctorForCheckup
        fields = ['id', 'name', 'visiting_charge']


class CheckupSerializer(serializers.ModelSerializer):
    doctors = DoctorForCheckupSerializer(many=True)
    payment_status = serializers.SerializerMethodField()
    total_payable = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    def get_id(self, checkup: models.Checkup):
        url = (
                reverse('store:orders-list')
                + str(checkup.id)
        )
        return format_html('<a href={}>📌({})</a>', url, checkup.id)

    def get_total_payable(self, checkup: models.Checkup):
        return sum([item.doctor_fees for item in checkup.doctors.all()])

    def get_payment_status(self, checkup: models.Checkup):
        if checkup.payment_status == checkup.PAYMENT_STATUS_PENDING:
            url = (
                    reverse('store:checkups-list')
                    + str(checkup.id)
                    + str('/payment/')
            )
            return format_html('<a href={}>👉Click to Pay!👈</a>', url)
        elif checkup.payment_status == checkup.PAYMENT_STATUS_FAILED:
            url = (
                    reverse('store:checkups-list')
                    + str(checkup.id)
                    + str('/payment/')
            )
            pay = format_html('<a href={}>👉Click Again to Pay!👈</a>', url)
            return format_html('<h5 style="color: RED">Payment Failed</h5><p>{}</p>', pay)
        else:
            return format_html('<h5 style="color: GREEN">Payment Successfull</h5>')

    class Meta:
        model = models.Checkup
        fields = ['id', 'booked_at', 'doctors', 'total_payable', 'payment_status']


class AddQuerySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        read_only=True,
        label='Save your unique query ID to get search answer later.'
    )

    class Meta:
        model = models.Query
        fields = ['id', 'name', 'phone', 'question']


class QuerySerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField()

    def get_question(self, query: models.Query):
        url = (
                reverse('store:querys-list')
                + str(query.id)
        )
        return format_html('<a href={}>{}</a>', url, query.question)

    class Meta:
        model = models.Query
        fields = ['name', 'question', 'answer']


class ReviewSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    test = serializers.SerializerMethodField()

    def get_test(self, review: models.Review):
        return review.test.title

    def get_name(self, review: models.Review):
        return review.user

    class Meta:
        model = models.Review
        fields = ['name', 'test', 'date', 'description']


class AddReviewSerializer(serializers.ModelSerializer):
    def save(self, **kwargs):
        self.instance = models.Review.objects.create(
            user_id=self.context['user_id'],
            test=self.validated_data['test'],
            description=self.validated_data['description']
        )
        return self.instance

    class Meta:
        model = models.Review
        fields = ['test', 'description']


class ReportSerializer(serializers.ModelSerializer):
    order = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    def get_id(self, report: models.Report):
        url = (
                reverse('store:reports-list')
                + str(report.id)
        )
        return format_html('<a href={}>📌({})</a>', url, report.id)

    def get_order(self, report: models.Report):
        return report.order.tests.test.title

    class Meta:
        model = models.Report
        fields = ['id', 'order', 'detail']