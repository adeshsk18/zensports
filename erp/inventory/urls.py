from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/new/', views.product_create, name='product_create'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('category/new/', views.category_create, name='category_create'),
] 