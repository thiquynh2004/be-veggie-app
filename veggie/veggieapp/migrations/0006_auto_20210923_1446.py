# Generated by Django 3.2.7 on 2021-09-23 07:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('veggieapp', '0005_alter_cartitem_subtotal'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cartitem',
            old_name='subtotal',
            new_name='total',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='quantity',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='total',
        ),
    ]
