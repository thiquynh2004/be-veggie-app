from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.urls import path
from django.utils.html import mark_safe
from django import forms
from .models import Category, Product, Cart, CartItem, Order, User, Tag, SalesPromotion
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class ProductForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Product
        fields = '__all__'


class ProductTagInline(admin.TabularInline):
    model = Product.tags.through


class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ["id", "name", "price", "discount", "origin", "quantity", "active", "salesPromotion"]
    search_fields = ["name", "price", "discount"]
    list_filter = ["name"]
    readonly_fields = ["avatar"]
    inlines = (ProductTagInline,)

    def avatar(self, product):  # nhớ kiểm tra nè
        return mark_safe(
            "<img src='/static/{img_url}' alt='{alt}' width='120px'/>".format(img_url=product.image.name,
                                                                              alt=product.name))


# xem lại nhá- Nhúng các mối quan hệ manytomany, manytoone
class ProductInline(admin.StackedInline):
    model = Product
    pk_name = ['category', 'salesPromotion']  # tên khóa ngoại


class CategoryAdmin(admin.ModelAdmin):
    inlines = [ProductInline]


class SalesPromotionAdmin(admin.ModelAdmin):
    inlines = [ProductInline]


admin.site.site_header = 'HỆ THỐNG BÁN HÀNG VEGGIE'
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(SalesPromotion, SalesPromotionAdmin)
admin.site.register(Order)
admin.site.register(Tag)
admin.site.register(User)
