from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'sku', 'description', 'price', 'stock', 'reorder_level']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'min': '0'}),
            'reorder_level': forms.NumberInput(attrs={'min': '0'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter unique SKU'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Add help text for reorder level
        self.fields['reorder_level'].help_text = "Minimum stock level before reordering"
        self.fields['sku'].help_text = "Unique identifier for the product"

    def clean_sku(self):
        sku = self.cleaned_data.get('sku')
        if Product.objects.filter(sku=sku).exists():
            raise ValidationError("This SKU already exists. Please use a different one.")
        return sku

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