from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import TokenRefreshView


router = DefaultRouter()
router.register('request-otp', views.RequestOtpApiView, basename='request_otp')
router.register('verify-otp', views.VerifyOtpApiView, basename='verify_otp')
router.register('login', views.LoginApiView, basename='login')
router.register('logout', views.LogoutApiView, basename='logout')
router.register('', views.ProfileApiView, basename='myuser')


urlpatterns = router.urls + [
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
]