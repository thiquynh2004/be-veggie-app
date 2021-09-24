from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('products', views.ProductViewSet, basename="products")
router.register('users', views.UserViewSet, basename="users")
router.register('categories', views.CategoryViewSet, basename="categories")
router.register('salesPromotions', views.SalesPromotionViewSet, basename="salesPromotion")
router.register('carts', views.CartViewSet, basename="carts")
router.register('cartitems', views.CartItemViewSet, basename="cartitems")
router.register('orders', views.OrderViewSet, basename="orders")


urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('oauth2-info/', views.AuthInfo.as_view()),
    path('add-to-cart', views.AddToCartView.as_view())
    # path('categories/', views.CategoryView.as_view())
    # re_path(r'^user/(?P<is_active>\w+)/$', UserViewSet.as_view()),
]
