from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View, FormView
from .models import Category, Product
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
import csv
from . tasks import generate_dummy_products_data
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

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category_form.html'
    success_url = reverse_lazy('product:category-list')

class CategoryDeleteView(LoginRequiredMixin,DeleteView):
    model = Category
    template_name = 'category_confirm_delete.html'
    success_url = reverse_lazy('product:category-list')
    
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
    
    
     # shana added 
    def get_queryset(self):
        user = self.request.user
        queryset = Product.objects.all().order_by('id')
        print("user=============", user.role)
        if user.role == 'agent':
            queryset = queryset.filter(created_by=user)
        elif user.role == 'staff' :
            queryset = queryset.filter(created_by=user)
        elif user.role == 'admin':
            queryset = queryset.all()
        return queryset
    

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('product:product-list')

   
    def form_valid(self, form):
        category_id = self.request.POST.get('category')
        print('category_id: ', category_id)
        if category_id == 'new':
            new_category_name = self.request.POST.get('new_category')
            category, created = Category.objects.get_or_create(name=new_category_name)
            form.instance.category = category
        else:
            form.instance.category_id = category_id
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    
class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('product:product-list')

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'product_confirm_delete.html'
    success_url = reverse_lazy('product:product-list')
    

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'
    
class ProductApprovalUpdateView(UpdateView):
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
    
    
class ExportProductsView(View):
    
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'
        writer = csv.writer(response)
        writer.writerow(['Title', 'Category', 'Description', 'Price', 'Status', 'Created At', 'Updated At', 'Created By'])
        
        products = Product.objects.all().select_related('category', 'created_by')
        for product in products:
            writer.writerow([product.title, product.category.name, product.description, product.price, product.get_status_display(), product.created_at, product.updated_at, product.created_by.username])
        
        return response
    
class GenerateDummyProductsView(FormView):
    template_name = 'generate_product_form.html'
    form_class = DummyProductForm
    success_url = reverse_lazy('product:product-list')
    
    
    def form_valid(self, form):
        num_products = form.cleaned_data['num_of_products']
        user_id = self.request.user.id
        generate_dummy_products_data.delay(num_products, user_id)
        messages.success(self.request, f'Started generating {num_products} dummy products.')
        return super().form_valid(form)