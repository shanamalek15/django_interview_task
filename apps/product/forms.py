from django import forms
from .models import Category, Product

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'title', 'description', 'price', 'video']


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