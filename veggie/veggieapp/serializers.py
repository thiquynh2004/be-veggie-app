from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.views import APIView

from .models import Product, User, Category, CartItem, Cart, Tag, SalesPromotion, Order
from django.conf import settings


class UserSerializer(ModelSerializer):
    # băm mật khẩu trước khi đăng kí user : ghi đè phương thức create
    # def create(self, validated_data):
    #     user = User(**validated_data)
    #     user.set_password(user.password)
    #     user.save()
    #
    #     return user
    #
    # class Meta:
    #     model = User
    #     fields = ["id", "first_name", "last_name", "email", "username",
    #               "password", "avatar", 'phone', 'address', 'date_joined']
    #     extra_kwargs = {
    #         'password': {'write_only': 'True'}  # sử dụng extra_kwargs để lấy thông tin của User mà k lấy mật khẩu
    #     }

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(user.password)
        user.save()

        return user

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name",
                  "username", "password", "email", "date_joined"]
        extra_kwargs = {
            'password': {'write_only': 'true'}
        }


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class ProductSerializer(ModelSerializer):
    # image = SerializerMethodField()

    # def get_image(self, product):
    #     request = self.context['request']
    #     name = product.image.name
    #     if name.startswith("static/"):
    #         path = '/%s' % name
    #     else:
    #         path = '/static/%s' % name
    #     return request.build_absolute_uri(path)

    tags = TagSerializer(many=True)
    category = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Product
        fields = ['category', 'id', 'name', 'image', 'price', 'discount', 'active', 'tags']


class SalesPromotionSerializer(ModelSerializer):
    class Meta:
        model = SalesPromotion
        fields = ['name', 'discounts', 'created_date', 'updated_date', 'active']


class CartItemSerializer(ModelSerializer):
    products = ProductSerializer(many=True)
    # user = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = CartItem
        fields = '__all__'
        depth = 1


# giỏ hàng nè
class CartSerializer(ModelSerializer):
    customer = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Cart
        fields = '__all__'
        depth = 1


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        depth = 1
