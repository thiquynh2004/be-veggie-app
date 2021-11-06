from ckeditor.fields import RichTextField
from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.reverse import reverse


class User(AbstractUser):
    address = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='uploads/%Y/%m')

    # def __str__(self):
    #     return self.username


# class Customer(models.Model):
class Category(models.Model):
    class Meta:
        ordering = ['-name']
    name = models.CharField(max_length=100, unique=True, null=False)

    def __str__(self):
        return self.name


class SalesPromotion(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    discounts = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    class Meta:
        ordering = ['-id']
        unique_together = ('name', 'category')

    category = models.ForeignKey(Category, related_name="products", on_delete=models.SET_NULL, null=True)
    salesPromotion = models.ForeignKey(SalesPromotion, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100, null=False)
    price = models.IntegerField()
    discount = models.IntegerField(default=0)
    origin = models.CharField(max_length=50, blank=True, null=True)
    description = RichTextField(null=True, blank=True)
    # quantity = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    slug = models.SlugField(null=True)
    inventory = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to='products/%Y/%m')
    tags = models.ManyToManyField('Tag', related_name="products", blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_discount(self):
        return self.salesPromotion.discounts

    # def get_absolute_url(self):
    #     return reverse("core:product", kwargs={
    #         'slug': self.slug
    #     })
    #
    # def get_add_to_cart_url(self):
    #     return reverse("core:add-to-cart", kwargs={
    #         'slug': self.slug
    #     })
    #
    # def get_remove_from_cart_url(self):
    #     return reverse("core:remove-from-cart", kwargs={
    #         'slug': self.slug
    #     })


class Tag(models.Model):
    name = models.CharField(max_length=50, blank=True, unique=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    # product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True, null=True)
    total = models.IntegerField(null=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.customer.username


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    products = models.ManyToManyField(Product)
    price = models.IntegerField()
    quantity = models.DecimalField(max_digits=5, decimal_places=2)
    total = models.IntegerField()

    def __str__(self):
        return f"Cart:{self.cart.customer.username}<=>Total=={self.total}"

    # def get_total_product_price(self):
    #     return self.quantity * self.product.price
    #
    # def get_total_product_discount(self):
    #     return self.quantity * self.product.discount
    #
    # def get_total_pay(self):
    #     return self.get_total_product_price() - self.get_total_product_discount()
    #
    # def get_total(self):
    #     if self.product.discount:
    #         return self.get_total_product_discount()
    #     return self.get_total_product_price()


OrderStatus = (
    ("Chờ xác nhận", "Chờ xác nhận"),
    ("Chờ lấy hàng", "Chờ lấy hàng"),
    ("Đang giao hàng", "Đang giao hàng"),
    ("Đã hoàn thành", "Đã hoàn thành")
)


class Order(models.Model):
    address = models.CharField(max_length=100)
    phoneNumber = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    discount = models.IntegerField()
    total = models.IntegerField()
    orderStatus = models.CharField(max_length=30, choices=OrderStatus, default="Chờ xác nhận")
    payment = models.BooleanField()
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.customer.username

    def get_total(self):
        total = 0
        for cart in self.cart.all():
            total += cart.get_price_pay
        return total
