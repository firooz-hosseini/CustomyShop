from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('categories',views.CategoryViewSet, basename='category')
router.register('products',views.ProductViewSet, basename='product')
router.register('product-images', views.ProductImageViewSet, basename='product_image')

urlpatterns = router.urls