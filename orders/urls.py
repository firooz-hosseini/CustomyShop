from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('mycart', views.CartApiView, basename='mycart')
router.register('orders', views.OrderViewSet, basename='orders')
router.register('payments', views.PaymentViewSet, basename='payments')


urlpatterns = router.urls