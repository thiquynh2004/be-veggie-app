# Generated by Django 3.2.7 on 2021-09-24 09:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('veggieapp', '0009_rename_product_cartitem_products'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='user',
            new_name='customer',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='user',
            new_name='customer',
        ),
    ]
