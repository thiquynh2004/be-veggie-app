from decimal import Decimal

from rest_framework import viewsets, permissions, status, generics, serializers, views
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from .paginator import BasePagination
from .serializers import *

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
    # @action(methods=['get'], detail=False, url_path="profile")
    # def profile(self, request):
    #     try:
    #         queryset = User.objects.get(customer=request.user)
    #         return Response(self.serializer_class(request.user).data,
    #                         status=status.HTTP_200_OK)
    #     except:
    #         return Response(status=status.HTTP_403_FORBIDDEN)


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
        return Response(ProductSerializer(products, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)


class ProductViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, ):
    queryset = Product.objects.filter(active=True)
    serializer_class = ProductSerializer
    pagination_class = BasePagination
    lookup_field = "id"

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


class SalesPromotionViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = SalesPromotion.objects.all()
    serializer_class = SalesPromotionSerializer


class CartViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.DestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    parser_classes = [MultiPartParser, JSONParser]
    permission_classes = [IsAuthenticated, ]

    # lay gio hang cua khach hang
    def list(self, request):
        try:
            queryset = Cart.objects.get(customer=request.user)
            return Response(CartSerializer(queryset, context={'request': request}).data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # xoa giỏ hàng
    def delete(self, request, *args, **kwargs):
        try:
            cart = Cart.objects.get(id=request.data['id'])
            cart.delete()
            return Response({'message': "Xóa giỏ hàng thành công"}, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # thêm sản phẩm vào giỏ hàng
    @action(methods=["post"], detail=False, url_path="add-to-cart", url_name="add-to-cart")
    def add_to_cart(self, request):
        product_id = request.data['id']
        product = get_object_or_404(Product, id=product_id)
        quantity = request.data['quantity']
        cart = Cart.objects.filter(customer=request.user, is_completed=False).first()
        try:
            # Nếu có cart
            if cart:
                _exit_cart_item = CartItem.objects.filter(cart=cart)
                flag = False
                # Nếu có list cartItem]
                if _exit_cart_item is not None:
                    # Duyệt qua các item trong list cartItem, mỗi item là 1 product
                    for item in _exit_cart_item:
                        pItem = item.products.all()[0]
                        if pItem == product:
                            flag = True
                            item.quantity += Decimal(quantity)
                            item.save()

                try:
                    if not flag:
                        try:
                            new_cart_item = CartItem.objects.create(
                                cart=cart,
                                price=product.price,
                                # discount=product.discount,
                                quantity=Decimal(quantity),

                                # total=Decimal(quantity) * (product.price - product.discount)
                                total=Decimal(quantity) * (product.price - product.discount * product.price * Decimal(0.01))
                            )
                        except Exception as e:
                            return Response(status=status.HTTP_400_BAD_REQUEST, data=(str)(e))
                        new_cart_item.products.add(product)
                        # cart.total += Decimal(quantity) * (product.price - product.discount)
                        cart.total += Decimal(quantity) * (product.price - product.discount * product.price * Decimal(0.01))

                        cart.save()
                except:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data="product new")

                # else:
                #     new_cart_item = CartItem.objects.create(
                #         cart=cart,
                #         price=product.price,
                #         discount=product.discount,
                #         quantity=quantity,
                #         total=quantity * (product.price - product.discount)
                #         # product=product,
                #         # customer=request.user,
                #         # cart__is_completed=False
                #     )
                #     new_cart_item.product.add(product)
                #     cart.total += quantity * (product.price - product.discount)
                #     cart.save()
                # new_cart_item.save()
            else:
                try:
                    Cart.objects.create(customer=request.user, total=0, is_completed=False)
                    newCart = Cart.objects.filter(customer=request.user, is_completed=False)
                    new_cartitem = CartItem.objects.create(
                        cart=newCart,
                        price=product.price,
                        # discount=product.discount,
                        quantity=Decimal(quantity),
                        total=Decimal(quantity) * (product.price - product.discount * product.price * Decimal(0.01))

                    )
                    new_cartitem.products.add(product)
                    # newCart.total += (product.price - product.discount) * Decimal(quantity)
                    newCart.total += Decimal(quantity) * (product.price - product.discount * product.price * Decimal(0.01))
                    newCart.save()
                except:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data="new cart")
            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# Xóa từng sản phẩm, update sản phẩm, xóa cả cartItems
class CartItemViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView, generics.RetrieveAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated, ]

    @action(methods=["post"], detail=True, url_path="update-cartitem", url_name="update-cartitem")
    def update_quantity(self, request, pk):
        cart_item = self.get_object()
        quantity = request.data.get("quantity")
        if Decimal(quantity) > 0.5:
            cart_item.quantity = Decimal(quantity)

            cart_item.save()
            return Response(self.serializer_class(cart_item).data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Chọn số kg lớn hơn 0.5"}, status=status.HTTP_400_BAD_REQUEST)


class AddToCartView(views.APIView):
    permission_classes = [IsAuthenticated, ]


#
#     def post(self, request):
#         product_id = request.data['id']
#         # # product = Product.objects.get(id=product_id)
#         product = get_object_or_404(Product, id=product_id)
#         quantity = request.data.get['quantity']
#         cart = Cart.objects.filter(customer=request.user, is_completed=False).first()
#         cart_items = CartItem.objects.filter(product__id=product_id).first()
#         # if quantity >= 0.5:
#         #     return quantity
#         try:
#             if cart:
#                 _exit_cart_item = cart.cartitem_set.filter(product=product)
#                 if _exit_cart_item.exits():
#                     cart_items = CartItem.objects.filter(product=product,
#                                                          customer=request.user,
#                                                          cart__is_completed=False)
#                     cart_items.quantity += quantity
#                     cart_items.save()
#                 else:
#                     new_cart_item = CartItem.objects.create(
#                         cart=cart,
#                         price=product.price,
#                         discount=product.discount,
#                         quantity=quantity,
#                         total=quantity * (product.price - product.discount)
#                         # product=product,
#                         # customer=request.user,
#                         # cart__is_completed=False
#                     )
#                     new_cart_item.product.add(product)
#                     cart.total += quantity * (product.price - product.discount)
#                     cart.save()
#                     # new_cart_item.save()
#             else:
#                 Cart.objects.create(customer=request.user, total=0, is_completed=False)
#                 newCart = Cart.objects.filter(customer=request.user, is_completed=False).first()
#                 new_cartitem = CartItem.objects.create(
#                     cart=newCart,
#                     price=product.price,
#                     discount=product.discount,
#                     quantity=quantity,
#                     total=quantity * (product.price - product.discount)
#
#                 )
#                 new_cartitem.products.add(product)
#                 newCart.total += (product.price - product.discount) * quantity
#                 newCart.save()
#             return Response(status=status.HTTP_201_CREATED)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)


class OrderViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.RetrieveAPIView,
                   generics.DestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permissions_class = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):

        try:
            queryset = Order.objects.filter(cart__customer=request.user)
            return Response(OrderSerializer(queryset, status=status.HTTP_200_OK))
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        cart_id = request.data["cartId"]
        cart = Cart.objects.get(id=cart_id)
        address = request.data["address"]
        phone = request.data["phone"]
        email = request.data["email"]
        createOrder = Order.objects.create(
            cart=cart,
            address=address,
            phone=phone,
            email=email,
            total=cart.total,

        )
        return Response(status=status.HTTP_201_CREATED)
