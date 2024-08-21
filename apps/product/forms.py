from django import forms
from .models import Category, Product
from django.core.exceptions import ValidationError

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'title', 'description', 'price', 'video']

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price < 0:
            raise ValidationError("Price cannot be negative.")
        return price
class ProductApprovalForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = [
            ('draft', 'Draft'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ]
        
        
class DummyProductForm(forms.Form):
    num_of_products = forms.IntegerField(min_value=1, label='Number of Dummy Products',
                                    required=True)