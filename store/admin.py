from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from . import models


@admin.register(models.Qualification)
class QualificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'doctors_count', 'name']
    list_per_page = 10
    search_fields = ['title', 'name']

    def doctors_count(self, qualification: models.Qualification):
        url = (
                reverse('admin:store_doctor_changelist')
                + '?'
                + urlencode({
                    'qualification_id': str(qualification.id)
                })
        )
        return format_html('<a href={}>{} Doctors</a>', url, qualification.doctors_count)

    def get_queryset(self, request):
        return super(QualificationAdmin, self).get_queryset(request).annotate(
            doctors_count=Count('doctor')
        )


@admin.register(models.Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'doctors_count']
    list_per_page = 10
    search_fields = ['title']

    def doctors_count(self, speciality: models.Department):
        url = (
            reverse('admin:store_doctor_changelist')
            + '?'
            + urlencode({
                'department_id': str(speciality.id)
             })
        )
        return format_html('<a href={}>{} Doctors</a>', url, speciality.doctors_count)

    def get_queryset(self, request):
        return super(DepartmentAdmin, self).get_queryset(request).annotate(
            doctors_count=Count('doctor')
        )

    def image_thumbnail(self, profile: models.Doctor):
        if profile.image.name != '':
            return format_html(
                f"<a href='{profile.image.url}'>"
                f"<img src='{profile.image.url}' "
                f"style='object-fit: cover; width: 125px; height: 125px;' "
                f"/>"
                f"</a>"
            )
        else:
            return ''


class TimingInline(admin.TabularInline):
    model = models.Timing
    min_num = 1
    extra = 0


@admin.register(models.Doctor)
class DoctorAdmin(admin.ModelAdmin):
    autocomplete_fields = ['qualification', 'department']
    list_display = ['first_name', 'last_name', 'qualification', 'department', 'fees', 'image_thumbnail']
    list_editable = ['fees']
    list_filter = ['department', 'qualification', 'last_update']
    list_per_page = 10
    inlines = [TimingInline]
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    def image_thumbnail(self, doctor: models.Doctor):
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


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'tests_count']
    list_per_page = 10
    search_fields = ['title']

    @admin.display(ordering='tests_count')
    def tests_count(self, collection: models.Collection):
        # reverse('admin:app_model_page')
        # app ---> what app are you working on
        # model ---> what is the target model
        # page ---> what is the target page, called 'changelist'
        url = (
                reverse('admin:store_test_changelist')
                + '?'
                + urlencode({
                    'collection_id': str(collection.id)
                 })
        )
        return format_html('<a href={}>{} Tests</a>', url, collection.tests_count)

    def get_queryset(self, request):
        return super(CollectionAdmin, self).get_queryset(request).annotate(
            tests_count=Count('test')
        )


class TestImageInline(admin.TabularInline):
    model = models.TestImage
    max_num = 3
    extra = 1
    readonly_fields = ['thumbnail']

    def thumbnail(self, test_image: models.TestImage):
        if test_image.image.name != '':
            return format_html(f"<img src='{test_image.image.url}' class='thumbnail' />")
        return ''


@admin.register(models.Test)
class TestAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    prepopulated_fields = {
        'slug': ['title', 'code']
    }
    list_display = ['title', 'code', 'collection_title', 'unit_price']
    list_editable = ['unit_price']
    list_filter = ['collection', 'last_update']
    list_select_related = ['collection']
    list_per_page = 10
    inlines = [TestImageInline]
    search_fields = ['title__istartswith']

    @admin.display(ordering='collection__title')
    def collection_title(self, test: models.Test):
        return test.collection.title

    class Media:
        css = {
            'all': ['store/styles.css']
        }


class OrderedTestsInline(admin.StackedInline):
    model = models.OrderedTest
    autocomplete_fields = ['test']
    min_num = 1
    max_num = 10
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user']
    inlines = [OrderedTestsInline]
    search_fields = ['id']
    list_display = ['id', 'placed_at', 'payment_status', 'user', 'report_status']       # 'ordered_tests_count']

    def report_status(self, order: models.Order):
        try:
            order.reports.get(order_id=order.id)
            return 'Created'
        except models.Report.DoesNotExist:
            url = reverse('admin:store_report_add')
            return format_html('<a href="{}">Create!</a>', url)

    # @admin.display(ordering='ordered_tests_count')
    # def ordered_tests_count(self, order: models.Order):
    #     return format_html('<a>{} Tests</a>', order.ordered_tests_count)

    def get_queryset(self, request):
        return super(OrderAdmin, self).get_queryset(request).\
            select_related('user', 'tests').annotate(ordered_tests_count=Count('tests'))


class DoctorForCheckupInline(admin.TabularInline):
    model = models.DoctorForCheckup
    autocomplete_fields = ['doctor']
    min_num = 1
    max_num = 10
    extra = 0


@admin.register(models.Checkup)
class CheckupAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user']
    inlines = [DoctorForCheckupInline]
    list_display = ['id', 'user', 'booked_at', 'payment_status', 'doctors_for_checkup']

    @admin.display(ordering='doctors_for_checkup')
    def doctors_for_checkup(self, checkup: models.Checkup):
        return format_html('<a>{} Doctors</a>', checkup.doctors_for_checkup)

    def get_queryset(self, request):
        return super(CheckupAdmin, self).get_queryset(request).annotate(
            doctors_for_checkup=Count('doctors')
        )


@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user', 'test']
    ordering = ['-date']
    list_display = ['user', 'test', 'description', 'date']


@admin.register(models.Query)
class QueryAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'phone', 'question', 'answer']
    list_editable = ['answer']
    list_per_page = 30
    ordering = ['-date']


@admin.register(models.Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'date']


@admin.register(models.Report)
class ReportAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.test = obj.order.tests.test
        obj.user = obj.order.user
        super(ReportAdmin, self).save_model(request, obj, form, change)

    def name(self, report: models.Report):
        return report.user

    autocomplete_fields = ['order']
    list_display = ['id', 'order', 'name', 'detail']
    readonly_fields = ['test', 'user']


