from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Product, Category
from .forms import ProductForm, CategoryForm
from django.contrib.auth.decorators import login_required
from django.db.models import F, Count

def index(request):
    """
    Display inventory overview with statistics and recent products
    """
    context = {
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'recent_products': Product.objects.select_related('category').order_by('-created_at')[:5],
        'low_stock_products': Product.objects.select_related('category').filter(
            stock__lte=F('reorder_level')
        ),
        'low_stock_count': Product.objects.filter(
            stock__lte=F('reorder_level')
        ).count(),
    }
    return render(request, 'inventory/index.html', context)

@login_required
def product_list(request):
    """
    Display list of all products
    """
    products = Product.objects.select_related('category').all()
    return render(request, 'inventory/product_list.html', {'products': products})

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
    categories = Category.objects.all().order_by('name')
    return render(request, 'inventory/category_list.html', {'categories': categories})

@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        try:
            Category.objects.create(name=name, description=description)
            messages.success(request, 'Category added successfully.')
        except Exception as e:
            messages.error(request, f'Error adding category: {str(e)}')
    return redirect('inventory:category_list')

@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        try:
            category.name = request.POST.get('name')
            category.description = request.POST.get('description')
            category.save()
            messages.success(request, 'Category updated successfully.')
        except Exception as e:
            messages.error(request, f'Error updating category: {str(e)}')
    return redirect('inventory:category_list')

@login_required
def delete_category(request, category_id):
    if request.method == 'POST':
        category = get_object_or_404(Category, id=category_id)
        try:
            category.delete()
            messages.success(request, 'Category deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting category: {str(e)}')
    return redirect('inventory:category_list')

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

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        try:
            product.delete()
            messages.success(request, 'Product deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting product: {str(e)}')
    return redirect('inventory:product_list')

@login_required
def stock_report(request):
    """
    Display stock report with low stock alerts
    """
    products = Product.objects.select_related('category').all()
    low_stock_products = products.filter(stock__lte=F('reorder_level'))
    
    context = {
        'products': products,
        'low_stock_products': low_stock_products,
        'low_stock_count': low_stock_products.count(),
    }
    return render(request, 'inventory/stock_report.html', context) 