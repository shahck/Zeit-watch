from django.urls import path
from . import views

urlpatterns = [
    path('',views.store,name='store'),
    path('category/<slug:category_slug>/',views.store,name='products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/',views.product_details,name='product_details'),
    path('search/', views.search, name='search'),
    # path('search/autocomplete', views.autocomplete, name='autocomplete'),

    # path('product-list', views.productlistAjax),
    # path('searchproduct', views.searchproduct, name="searchproduct"),

    path('submit_review/<int:product_id>/',views.submit_review,name='submit_review'),
]