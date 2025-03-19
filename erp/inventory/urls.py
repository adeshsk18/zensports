from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Overview/Index
    path('', views.index, name='index'),
    
    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='add_product'),
    path('products/<int:pk>/edit/', views.product_detail, name='edit_product'),
    path('products/<int:pk>/delete/', views.product_delete, name='delete_product'),
    path('products/<int:pk>/update-stock/', views.update_stock, name='update_stock'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/<int:category_id>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    
    # Stock Report
    path('stock-report/', views.stock_report, name='stock_report'),
] 