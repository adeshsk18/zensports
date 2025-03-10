from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Product, Category
from .forms import ProductForm, CategoryForm
from django.contrib.auth.decorators import login_required
from django.db.models import F

@login_required
def product_list(request):
    products = Product.objects.all()
    low_stock_products = Product.objects.filter(stock__lte=F('minimum_stock'))
    context = {
        'products': products,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'inventory/product_list.html', context)

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('inventory:product_list')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'title': 'Edit Product'
    }
    return render(request, 'inventory/product_form.html', context)

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Product created successfully!')
            return redirect('inventory:product_list')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'New Product'
    }
    return render(request, 'inventory/product_form.html', context)

@login_required
def update_stock(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        quantity = int(request.POST.get('quantity', 0))
        product.stock += quantity
        product.save()
        return JsonResponse({'success': True, 'new_stock': product.stock})
    return JsonResponse({'success': False}, status=400)

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'inventory/category_list.html', {'categories': categories})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('inventory:category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'inventory/category_form.html', {'form': form}) 