# Generated by Django 3.2.7 on 2021-09-23 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('veggieapp', '0007_remove_cart_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total',
            field=models.IntegerField(),
        ),
    ]