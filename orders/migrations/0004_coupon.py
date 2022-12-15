# Generated by Django 4.1.3 on 2022-12-06 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_alter_order_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coupon_code', models.CharField(max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('minimum_amount', models.IntegerField(default=999)),
                ('discount_price', models.IntegerField(default=199)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('modify_date', models.DateTimeField(auto_now=True)),
                ('expiry_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
