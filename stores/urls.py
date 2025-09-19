from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register('myuser/register_as_seller', views.SellerRequestViewSet, basename='seller_requests')
router.register('mystore', views.StoreApiViewSet, basename='mystore')


urlpatterns = router.urls 