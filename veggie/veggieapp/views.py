from django.conf import settings
from django.http import HttpResponse, Http404
from rest_framework import viewsets, permissions, status, generics, serializers, views
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from .models import Product, User, Category, Cart, CartItem, SalesPromotion, Order
from .paginator import BasePagination
from .serializers import (ProductSerializer, UserSerializer,
                          CategorySerializer, CartSerializer, CartItemSerializer, SalesPromotionSerializer,
                          OrderSerializer)
# ProductDetailSerializer)

from django.shortcuts import render, get_object_or_404
from django.views import View


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, JSONParser]

    def get_permissions(self):  # retrieve : lấy thông tin cụ thể mặc định là user được chứng thực
        if self.action == 'get_current_user':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    # lấy thông tin current_user

    @action(methods=['get'], detail=False, url_path="current-user")
    def get_current_user(self, request):
        return Response(self.serializer_class(request.user).data, status=status.HTTP_200_OK)

    # queryset = User.objects.filter(is_active=True)
    # serializer_class = UserSerializer
    #
    # def get_permissions(self):
    #     if self.action == 'get_current_user':
    #         return [permissions.IsAuthenticated()]
    #
    #     return [permissions.AllowAny()]
    #
    # @action(methods=['get'], detail=False, url_path="current-user")
    # def get_current_user(self, request):
    #     return Response(self.serializer_class(request.user).data,
    #                     status=status.HTTP_200_OK)
class AuthInfo(APIView):
    def get(self, request):
        return Response(settings.OAUTH2_INFO, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    # lay ds san pham cua mot loai san pham
    @action(methods=['get'], detail=True, url_path='products')
    def get_products(self, request, pk):
        # category = Category.objects.get(pk=pk)
        # products = category.products.filter(active=True)
        products = self.get_object().products.filter(active=True)
        keyword = request.query_params.get('keyword')
        if keyword is not None:
            products = products.filter(name__icontains=keyword)
        return Response(ProductSerializer(products, many=True).data, status=status.HTTP_200_OK)


class ProductViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, ):
    queryset = Product.objects.filter(active=True)
    serializer_class = ProductSerializer
    pagination_class = BasePagination

    # tim kiem san pham dua theo cate_id va theo ten
    def get_queryset(self):
        product = Product.objects.filter(active=True)
        q = self.request.query_params.get('q')
        if q is not None:
            product = product.filter(name__icontains=q)
        cate_id = self.request.query_params.get('category_id')
        if cate_id is not None:
            product = product.filter(category_id=cate_id)
        return product

    # permission_classes = [permissions.IsAuthenticated]
    @action(methods='get', detail=False, url_path='get-product', url_name="Get-product")
    def get_product(self, request, pk=None):
        if pk:
            return self.retrieve(request)
        else:
            return self.list(request)

    @action(methods=['post'], detail=True,
            url_path="hide-product", url_name="Hide-product")
    def hide_lesson(self, request, pk):
        try:
            p = Product.objects.get(pk=pk)
            p.active = False
            p.save()
        except Product.DoesNotExits:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(data=ProductSerializer(p, context={'request': request}).data,
                        status=status.HTTP_200_OK)


class SalesPromotionViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = SalesPromotion.objects.all()
    serializer_class = SalesPromotionSerializer


class CartViewSet(viewsets.ViewSet,
                  generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    parser_classes = [MultiPartParser, JSONParser]
    permission_classes = [IsAuthenticated, ]

    # tạo giỏ hàng
    # xóa giỏ hàng
    def destroy(self, request, *args, **kwargs):
        if request.user == self.get_object().customer:
            return super().destroy(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)

    # cập nhật giỏ hàng
    def put(self, request, *args, **kwargs):
        if request.user == self.get_object().customer:
            return super().destroy(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)


class CartItemViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.UpdateAPIView,
                      generics.RetrieveAPIView, generics.DestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated, ]

    # cập nhật giỏ hàng
    def put(self, request, *args, **kwargs):
        if request.user == self.get_object().customer:
            cartitem = CartItem.objetcs.get(id=request.data["id"])
            cart = cartitem.cart
            product = Product.objects.get(active=True)
            if cartitem.quantity >= 0.5:
                cartitem.quantity = cartitem.quantity
                cartitem.price += (cartitem.quantity * cartitem.price)
                cartitem.total += (cartitem.price - cartitem.quantity * product.discount)
                cartitem.save()

            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    #xóa item

    def delete(self, request, *args, **kwargs):
        if request.user == self.get_object().customer:
            return super().delete(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        if slug is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        product = request.data.get('product_id')
        cart = Cart.objects.filter(customer=request.user, is_completed=False)
        cartitem = CartItem.objects.filter(product_id=product.id).first()
        dfquantity = 0
        if dfquantity >= 0.5:
            return dfquantity
        try:
            if cart:
                _exit_cartitem = cart.cartitem_set.filter(product)
                if _exit_cartitem.exits():
                    cartitem = CartItem.objects.filter(product=product,
                                                       customer=request.user,
                                                       cart__is_completed=False)
                    cartitem.quantity += dfquantity
                    cartitem.save()
                else:
                    cartitem = CartItem.objects.create(
                        product=product,
                        customer=request.user,
                        cart__is_completed=False
                    )
                    cartitem.save()
            else:
                Cart.objects.create(customer=request.user, total=0, is_completed=False)
                newCart = Cart.objects.filter(customer=request.user, is_completed=False).first()
                newCartItem = CartItem.objects.create(
                    cart=newCart,
                    price=product.price,
                    quantity=dfquantity,
                    total=product.price * dfquantity,

                )
                newCartItem.add(product)
                newCart.total += (product.price - product.discount) * dfquantity
                newCart.save()
            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class OrderViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.DestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permissions_class = [IsAuthenticated, ]
