from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
# Create your views here.
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import *
from .models import Category, Product
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
import csv
from . tasks import generate_dummy_products_data
from django.utils.decorators import method_decorator
from .permissions import *
# Category Views
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'
    paginate_by = 10
    
class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category_form.html'
    success_url = reverse_lazy('product:category-list')
    
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
@method_decorator(can_update_delete_category_view, name='dispatch')
class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category_form.html'
    success_url = reverse_lazy('product:category-list')
    
@method_decorator(can_update_delete_category_view, name='dispatch')
class CategoryDeleteView(LoginRequiredMixin,DeleteView):
    model = Category
    template_name = 'category_confirm_delete.html'
    success_url = reverse_lazy('product:category-list')
    
@method_decorator(can_update_delete_category_view, name='dispatch')
class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'category_detail.html'
    context_object_name = 'category'
    
# Product Views
class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Product.objects.all().order_by('id')
        elif user.role == 'staff':
            # Staff can see their own products and products created by agents
            return Product.objects.filter(created_by__role='agent').order_by('id') | Product.objects.filter(created_by=user).order_by('id')
        else:  # For agents
            return Product.objects.filter(created_by=user).order_by('id')
    
class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('product:product-list')

   
    def form_valid(self, form):
        category_id = self.request.POST.get('category')
        form.instance.category_id = category_id
        form.instance.created_by = self.request.user

        # Set the product status based on the user's role
        if self.request.user.role in ['admin', 'staff']:
            form.instance.status = 'approved'
        else:
            form.instance.status = 'draft'

        return super().form_valid(form)

@method_decorator(can_update_delete_view_product, name='dispatch')
class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('product:product-list')

@method_decorator(can_update_delete_view_product, name='dispatch')
class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'product_confirm_delete.html'
    success_url = reverse_lazy('product:product-list')
    
@method_decorator(can_update_delete_view_product, name='dispatch')
class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

@method_decorator(can_give_approval_product, name='dispatch')
class ProductApprovalUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductApprovalForm
    template_name = 'product_approval_update.html'
    success_url = reverse_lazy('product:product-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        status = form.cleaned_data['status']
        if status == 'approved':
            messages.success(self.request, f'Product "{self.object.title}" has been approved.')
        elif status == 'rejected':
            messages.success(self.request, f'Product "{self.object.title}" has been rejected.')
        return response
    
    
class ExportProductsView(LoginRequiredMixin, View):
    
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'
        writer = csv.writer(response)
        writer.writerow(['Title', 'Category', 'Description', 'Price', 'Status', 'Created By'])
        if request.user.role == 'admin':
            products =  Product.objects.all().order_by('id')
        elif request.user.role == 'staff':
            # Staff can see their own products and products created by agents
            products =  Product.objects.filter(created_by__role='agent').order_by('id') | Product.objects.filter(created_by=user).order_by('id')
        else:  # For agents
            products = Product.objects.filter(created_by=request.user).order_by('id')
    
        products = Product.objects.all().select_related('category', 'created_by')
        for product in products:
            writer.writerow([product.title, product.category.name, product.description, product.price,
                             product.get_status_display(),  product.created_by.email])
        
        return response
    
class GenerateDummyProductsView(LoginRequiredMixin, FormView):
    template_name = 'generate_product_form.html'
    form_class = DummyProductForm
    success_url = reverse_lazy('product:product-list')
    
    
    def form_valid(self, form):
        num_products = form.cleaned_data['num_of_products']
        user_id = self.request.user.id
        generate_dummy_products_data.delay(num_products, user_id)
        messages.success(self.request, f'Started generating {num_products} dummy products.')
        return super().form_valid(form)
    
@method_decorator(can_give_approval_product, name='dispatch')
class ProductApprovalView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        new_status = request.POST.get('status')
        
        product = get_object_or_404(Product, id=product_id)
        
        if new_status in dict(Product.upload_status).keys():
            product.status = new_status
            product.save()
            return JsonResponse({'success': True, 'status': new_status})
        return JsonResponse({'success': False, 'error': 'Invalid status'})