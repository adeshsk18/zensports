from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.invoice_list, name='invoice_list'),
    path('create/', views.create_invoice, name='create_invoice'),
    path('generate-pdf/<int:invoice_id>/', views.generate_pdf, name='generate_pdf'),
    path('delete/<int:invoice_id>/', views.delete_invoice, name='delete_invoice'),
] 