from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Customer
from .forms import CustomerForm
from django.contrib.auth.decorators import login_required

@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by('name')
    return render(request, 'customers/customer_list.html', {'customers': customers})

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    invoices = customer.invoices.all().order_by('-invoice_date')
    return render(request, 'customers/customer_detail.html', {
        'customer': customer,
        'invoices': invoices
    })

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer created successfully.')
            return redirect('customers:customer_list')
    else:
        form = CustomerForm()
    return render(request, 'customers/customer_form.html', {'form': form})

@login_required
def delete_customer(request, pk):
    if request.method == 'POST':
        customer = get_object_or_404(Customer, pk=pk)
        try:
            customer.delete()
            messages.success(request, 'Customer deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting customer: {str(e)}')
    return redirect('customers:customer_list') 