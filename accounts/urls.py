from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register('request-otp', views.RequestOtpView, basename='request_otp')





urlpatterns = router.urls 