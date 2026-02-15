from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'courses', api_views.CourseViewSet, basename='course')
router.register(r'enrollments', api_views.EnrollmentViewSet, basename='enrollment')

urlpatterns = [
    path('', include(router.urls)),
]
