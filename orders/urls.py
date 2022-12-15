from django.urls import path
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payment/', views.payment, name='payment'),
    path('status/', views.payment_status, name='payment_status'),
    path('success/', views.payment_success, name='payment_success'),
    path('fail/', views.payment_fail, name='payment_fail'),

    path('apply-coupon/', views.apply_coupon, name="apply_coupon"),

]
