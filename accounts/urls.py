from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import TokenRefreshView


router = DefaultRouter()
router.register('accounts/request-otp', views.RequestOtpApiView, basename='request_otp')
router.register('accounts/verify-otp', views.VerifyOtpApiView, basename='verify_otp')
router.register('accounts/login', views.LoginApiView, basename='login')
router.register('accounts/logout', views.LogoutApiView, basename='logout')
router.register('', views.ProfileApiView, basename='myuser')
router.register('myuser/address', views.UserAddressApiView, basename='user_address')


urlpatterns = router.urls + [
    path('accounts/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
]