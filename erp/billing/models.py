from django.db import models
from customers.models import Customer
from inventory.models import Product

class Invoice(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='invoices')
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField()
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"INV-{self.invoice_number} - Rs. {self.total:,.2f}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last_invoice = Invoice.objects.order_by('-invoice_number').first()
            if last_invoice:
                # Extract the numeric part and increment
                try:
                    last_number = int(last_invoice.invoice_number)
                    self.invoice_number = str(last_number + 1).zfill(6)
                except ValueError:
                    self.invoice_number = "000001"
            else:
                self.invoice_number = "000001"
        super().save(*args, **kwargs)

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
