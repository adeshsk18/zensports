from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Category

class ProductForm(forms.ModelForm):
    delete_image = forms.BooleanField(required=False, initial=False)
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'sku', 'description', 'price', 'stock', 'reorder_level', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'min': '0'}),
            'reorder_level': forms.NumberInput(attrs={'min': '0'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter unique SKU'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Add help text for reorder level
        self.fields['reorder_level'].help_text = "Minimum stock level before reordering"
        self.fields['sku'].help_text = "Unique identifier for the product"
        self.fields['image'].help_text = "Upload a product image (optional)"
        
        # Make SKU readonly when editing
        if self.instance and self.instance.pk:
            self.fields['sku'].widget.attrs['readonly'] = True
            self.fields['sku'].help_text = "SKU cannot be changed after creation"

    def clean_sku(self):
        sku = self.cleaned_data.get('sku')
        # Skip SKU validation if we're editing an existing product
        if self.instance and self.instance.pk:
            return self.instance.sku
        # Only validate SKU uniqueness for new products
        if Product.objects.filter(sku=sku).exists():
            raise ValidationError("This SKU already exists. Please use a different one.")
        return sku

    def save(self, commit=True):
        product = super().save(commit=False)
        # Handle image deletion
        if self.cleaned_data.get('delete_image'):
            product.image = None
        if commit:
            product.save()
        return product

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'}) 