from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('mycart', views.CartApiView, basename='mycart')


urlpatterns = router.urls