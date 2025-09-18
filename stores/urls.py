from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
# router.register('accounts/request-otp', views.RequestOtpApiView, basename='request_otp')


urlpatterns = router.urls 