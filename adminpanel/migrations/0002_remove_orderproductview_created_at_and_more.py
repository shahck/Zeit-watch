# Generated by Django 4.1.3 on 2022-12-05 12:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderproductview',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='orderproductview',
            name='ordered',
        ),
        migrations.RemoveField(
            model_name='orderproductview',
            name='product_price',
        ),
        migrations.RemoveField(
            model_name='orderproductview',
            name='updated_at',
        ),
        migrations.RemoveField(
            model_name='orderproductview',
            name='user',
        ),
        migrations.RemoveField(
            model_name='orderproductview',
            name='variation',
        ),
    ]
