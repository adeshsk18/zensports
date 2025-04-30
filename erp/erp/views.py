from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import F
from inventory.models import Product, Category
from customers.models import Customer
from billing.models import Invoice
from django.contrib.auth import logout

@login_required
def dashboard(request):
    context = {
        'products': Product.objects.all().order_by('-created_at')[:5] if Product.objects.exists() else [],
        'low_stock_products': Product.objects.filter(stock__lte=F('reorder_level')) if Product.objects.exists() else [],
        'customers': Customer.objects.all().order_by('-created_at')[:5] if Customer.objects.exists() else [],
        'recent_invoices': Invoice.objects.all().order_by('-created_at')[:5] if Invoice.objects.exists() else [],
        'categories': Category.objects.all() if Category.objects.exists() else [],
    }
    return render(request, 'dashboard.html', context)

def custom_logout(request):
    logout(request)
    return redirect('login') 