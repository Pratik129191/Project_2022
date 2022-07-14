from django.contrib.auth.decorators import login_required
from django.urls import path, include
from rest_framework_nested import routers
from . import views

app_name = 'store'

router = routers.DefaultRouter()
router.register('collections', views.CollectionViewSet, basename='collections')
router.register('departments', views.DepartmentViewSet, basename='departments')
router.register('tests', views.TestViewSet, basename='tests')
router.register('doctors', views.DoctorViewSet, basename='doctors')
router.register('orders', views.OrderViewSet, basename='orders')
router.register('checkups', views.CheckupViewSet, basename='checkups')
router.register('querys', views.QueryViewSet, basename='querys')
router.register('reviews', views.ReviewViewSet, basename='reviews')
router.register('reports', views.ReportViewSet, basename='reports')

# tests_router = routers.NestedDefaultRouter(router, 'tests', lookup='test')
# tests_router.register('images', views.TestImageViewSet, basename='test-images')


urlpatterns = [

] + router.urls
