from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from .models import Invoice, InvoiceItem
from inventory.models import Product
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from decimal import Decimal
import json
from customers.models import Customer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime, timedelta
import os
import traceback

# Create your views here.

@login_required
def create_invoice(request):
    if request.method == 'POST':
        try:
            customer_id = request.POST.get('customer')
            invoice_date = request.POST.get('invoice_date')
            
            # Create invoice
            invoice = Invoice.objects.create(
                customer_id=customer_id,
                invoice_date=invoice_date,
                subtotal=Decimal('0.00'),
                tax=Decimal('0.00'),
                total=Decimal('0.00')
            )
            
            # Process products
            products = request.POST.getlist('product[]')
            quantities = request.POST.getlist('quantity[]')
            
            subtotal = Decimal('0.00')
            for product_id, quantity in zip(products, quantities):
                if product_id and quantity:
                    product = Product.objects.get(id=product_id)
                    quantity = int(quantity)
                    unit_price = product.price
                    total_price = unit_price * quantity
                    
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=total_price
                    )
                    
                    # Update product stock
                    product.stock -= quantity
                    product.save()
                    
                    subtotal += total_price
            
            # Update invoice totals
            tax = subtotal * Decimal('0.10')  # 10% tax
            total = subtotal + tax
            
            invoice.subtotal = subtotal
            invoice.tax = tax
            invoice.total = total
            invoice.save()
            
            messages.success(request, 'Invoice created successfully!')
            
            # Redirect to the invoice list page instead of showing the invoice template
            return redirect('billing:invoice_list')
            
        except Exception as e:
            # Print traceback to console for debugging
            traceback.print_exc()
            
            # Get the error message without string concatenation
            error_message = str(e)
            messages.error(request, f'Error creating invoice: {error_message}')
            return redirect('billing:create_invoice')
    
    context = {
        'customers': Customer.objects.all(),
        'products': Product.objects.filter(stock__gt=0)
    }
    return render(request, 'billing/create_invoice.html', context)

@login_required
def generate_pdf(request, invoice_id):
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id)
        format_type = request.GET.get('format', 'pdf')
        
        if format_type == 'html':
            # Get invoice items with related product data
            invoice_items = invoice.items.all().select_related('product')
            
            # Calculate due date
            due_date = invoice.invoice_date + timedelta(days=30)
            
            context = {
                'invoice': invoice,
                'invoice_items': invoice_items,
                'company_name': 'ZEN SPORTS',
                'company_address': '123 Sports Complex, MG Road',
                'company_city': 'Bangalore, Karnataka 560001',
                'company_phone': '+91 80 1234 5678',
                'company_email': 'info@zensports.com',
                'company_gst': '29ABCDE1234F1Z5',
                'auto_print': request.GET.get('print', 'false').lower() == 'true',
                'due_date': due_date
            }
            
            response = render(request, 'billing/invoice_template.html', context)
            response['X-Frame-Options'] = 'SAMEORIGIN'  # Allow iframe loading
            return response
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
        
        doc = SimpleDocTemplate(
            response,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Add custom styles
        styles.add(ParagraphStyle(
            name='CompanyName',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=20,
        ))
        
        styles.add(ParagraphStyle(
            name='CompanyInfo',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.gray,
            spaceAfter=3,
        ))
        
        styles.add(ParagraphStyle(
            name='InvoiceInfo',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=6,
        ))
        
        # Company Header with better alignment
        elements.append(Paragraph("ZEN SPORTS", styles['CompanyName']))
        company_info = [
            "123 Sports Complex, MG Road",
            "Bangalore, Karnataka 560001",
            "Tel: +91 80 1234 5678 | Email: info@zensports.com",
            "GST: 29ABCDE1234F1Z5",
        ]
        
        for info in company_info:
            elements.append(Paragraph(info, styles['CompanyInfo']))
        
        elements.append(Spacer(1, 30))
        
        # Invoice Details Table with invoice number
        invoice_info = [
            [Paragraph("<b>INVOICE</b>", styles['InvoiceInfo']), 
             Paragraph(f"<b>Invoice No:</b> INV-{invoice.invoice_number}", styles['InvoiceInfo']), 
             Paragraph(f"<b>Date:</b> {invoice.invoice_date.strftime('%d-%m-%Y')}", styles['InvoiceInfo'])],
            ["", "", 
             Paragraph(f"<b>Due Date:</b> {(invoice.invoice_date + timedelta(days=30)).strftime('%d-%m-%Y')}", styles['InvoiceInfo'])],
        ]
        
        t = Table(invoice_info, colWidths=[doc.width/3.0]*3)
        t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor('#000000')),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
        
        # Bill To Section
        elements.append(Paragraph("<b>BILL TO</b>", styles['InvoiceInfo']))
        customer_info = [
            Paragraph(invoice.customer.name, styles['Normal']),
            Paragraph(invoice.customer.address, styles['Normal']),
            Paragraph(f"Phone: {invoice.customer.phone}", styles['Normal']),
            Paragraph(f"Email: {invoice.customer.email}", styles['Normal']),
        ]
        
        for info in customer_info:
            elements.append(info)
        
        elements.append(Spacer(1, 20))
        
        # Items Table with better styling
        items_data = [[
            Paragraph("<b>Item Description</b>", styles['Normal']),
            Paragraph("<b>Qty</b>", styles['Normal']),
            Paragraph("<b>Rate</b>", styles['Normal']),
            Paragraph("<b>Amount</b>", styles['Normal'])
        ]]
        
        for item in invoice.items.all():
            items_data.append([
                Paragraph(item.product.name, styles['Normal']),
                str(item.quantity),
                f"Rs. {item.unit_price:,.2f}",
                f"Rs. {item.total_price:,.2f}"
            ])
        
        # Add subtotal, tax, and total with proper alignment
        items_data.extend([
            ["", "", Paragraph("<b>Subtotal:</b>", styles['Normal']), f"Rs. {invoice.subtotal:,.2f}"],
            ["", "", Paragraph("<b>GST (10%):</b>", styles['Normal']), f"Rs. {invoice.tax:,.2f}"],
            ["", "", Paragraph("<b>Total:</b>", styles['Normal']), f"Rs. {invoice.total:,.2f}"],
        ])
        
        # Create items table with better styling
        items_table = Table(items_data, colWidths=[doc.width/2.0, doc.width/6.0, doc.width/6.0, doc.width/6.0])
        items_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, len(items_data)-4), 0.5, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('LINEABOVE', (2, -3), (-1, -3), 0.5, colors.grey),
            ('LINEABOVE', (2, -1), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))
        elements.append(items_table)
        
        elements.append(Spacer(1, 30))
        
        # Terms and Bank Details in two columns
        terms_and_bank = [
            [Paragraph("<b>Terms & Conditions:</b>", styles['Normal']),
             Paragraph("<b>Bank Details:</b>", styles['Normal'])],
            [Paragraph("""1. Payment is due within 30 days<br/>
                         2. Goods once sold cannot be returned<br/>
                         3. All disputes are subject to Bangalore jurisdiction""",
                       styles['Normal']),
             Paragraph("""Bank Name: HDFC Bank<br/>
                         Account Name: Zen Sports<br/>
                         Account No.: 1234 5678 9012<br/>
                         IFSC Code: HDFC0001234""",
                       styles['Normal'])],
        ]
        
        terms_table = Table(terms_and_bank, colWidths=[doc.width/2.0]*2)
        terms_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(terms_table)
        
        doc.build(elements)
        return response
    except Exception as e:
        messages.error(request, f'Error generating PDF: {str(e)}')
        return redirect('billing:invoice_list')

@login_required
def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-invoice_date')
    return render(request, 'billing/invoice_list.html', {'invoices': invoices})

@login_required
def delete_invoice(request, invoice_id):
    if request.method == 'POST':
        invoice = get_object_or_404(Invoice, id=invoice_id)
        try:
            # Simply delete the invoice without restoring stock
            invoice.delete()
            messages.success(request, 'Invoice deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting invoice: {str(e)}')
    return redirect('billing:invoice_list')

@login_required
def update_status(request, invoice_id):
    if request.method == 'POST':
        invoice = get_object_or_404(Invoice, id=invoice_id)
        status = request.POST.get('status', '').upper()
        
        if status in ['PENDING', 'PAID']:
            invoice.payment_status = status
            invoice.save()
            
            return JsonResponse({
                'success': True,
                'status': status.lower(),
                'status_display': invoice.get_payment_status_display()
            })
    
    return JsonResponse({'success': False}, status=400)
