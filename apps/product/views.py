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
from . tasks import generate_dummy_products_data, upload_video_task
from django.utils.decorators import method_decorator
from .permissions import *
import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os
from .serializer import *
from rest_framework.generics import ListCreateAPIView
from django.db.models import Q
from django.utils import timezone

# Category Views
@method_decorator(agent_restriction, name='dispatch')
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'
    paginate_by = 10
    
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Category.objects.all().order_by('id')
        elif user.role == 'staff':
            # Staff can see their own products and products created by agents
            return Category.objects.filter(created_by__role='agent').order_by('id') \
                | Category.objects.filter(created_by=user).order_by('id')
        else:  # For agents
            return []

@method_decorator(agent_restriction, name='dispatch')
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
    # paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Product.objects.all().order_by('id')
        elif user.role == 'staff':
            return Product.objects.filter(created_by__role='agent').order_by('id') | Product.objects.filter(created_by=user).order_by('id')
        else:  # For agents
            return Product.objects.filter(created_by=user).order_by('id')
    
class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('product:product-list')

   
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        # Set the product status based on the user's role
        if self.request.user.role in ['admin']:
            form.instance.status = 'approved'
        else:
            form.instance.status = 'draft'
        product = form.save()
        video_file = self.request.FILES.get('video')
        if video_file:
            mime_type, _ = mimetypes.guess_type(video_file.name)
            print('mime_type: ', mime_type)
            if mime_type and mime_type.startswith('video'):
                try:
                    upload_video_task.delay(product.id, video_file.read(), video_file.name)
                    return JsonResponse({'status': 'success', 'message': 'Product Created'}, status=200)
                except Exception as e:
                    return JsonResponse({'status': 'error', 'message': f'Product created but video processing failed: {str(e)}'}, status=500)

        return JsonResponse({'status': 'success', 'message': 'Product Created'}, status=200)
        
    def form_invalid(self, form):
        return JsonResponse({'errors': form.errors}, status=400)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
        
@method_decorator(can_update_delete_view_product, name='dispatch')
class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('product:product-list')

    def form_valid(self, form):
        if form.instance.status == 'rejected':
            form.instance.status = 'draft'
        product = form.save()
        video_file = self.request.FILES.get('video')
        if video_file:
            mime_type, _ = mimetypes.guess_type(video_file.name)
            print('mime_type: ', mime_type)
            if mime_type and mime_type.startswith('video'):
                try:
                    upload_video_task.delay(product.id, video_file.read(), video_file.name)
                    return JsonResponse({'status': 'success', 'message': 'Product Updated'}, status=200)
                except Exception as e:
                    return JsonResponse({'status': 'error', 'message': f'Product Updated but video processing failed: {str(e)}'}, status=500)

        return JsonResponse({'status': 'success', 'message': 'Product Updated'}, status=200)

    def form_invalid(self, form):
        return JsonResponse({'errors': form.errors}, status=400)
    
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

        # Return a JSON response for AJAX
        return JsonResponse({
            'success': True,
            'message': f'Started generating {num_products} dummy products.'
        })

    def form_invalid(self, form):
        # Return errors as JSON
        return JsonResponse({
            'success': False,
            'message': form.errors.as_json()
        })
    
@method_decorator(can_give_approval_product, name='dispatch')
class ProductApprovalView(LoginRequiredMixin, View):
    
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        new_status = request.POST.get('status')
        rejection_reason = request.POST.get('rejection_reason', '')
        

        product = get_object_or_404(Product, id=product_id)
        product.approved_by = None  # Clear approval details
        product.approved_at = None
        product.rejected_by = None  # Clear rejection details
        product.rejected_at = None
        print('product: ', product)
        print("Request user", request.user.role)
        if request.user.role == 'staff' and product.created_by == request.user:
            return JsonResponse({'success': False, 'error': 'Only Officer allow for Rejection/Approval'}, status=400)
        
        if new_status in dict(Product.upload_status).keys():
            # Handle rejection
            if new_status == 'rejected':
                if not rejection_reason:
                    return JsonResponse({'success': False, 'error': 'Rejection reason is required'}, status=400)
                product.rejection_reason = rejection_reason
                product.rejected_by = request.user
                product.rejected_at = timezone.now()
                product.approved_by = None  # Reset approval if previously approved

            # Handle approval
            elif new_status == 'approved':
                product.approved_by = request.user
                product.approved_at = timezone.now()
                product.rejected_by = None  # Reset rejection if previously rejected
                product.rejection_reason = ''

            # Update product status and save
            product.status = new_status
            product.save()
            return JsonResponse({'success': True, 'status': new_status}, status=200)
        return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
    
    
class EncryptionView(View):

    def get(self, request):
        return render(request, 'encyption_view.html')


def encrypt_aes(plain_text, key):
    try:
        cipher = AES.new(key, AES.MODE_ECB)
        padding_length = 16 - (len(plain_text) % 16)
        padded_plain_text = plain_text + (chr(padding_length) * padding_length)
        encrypted_data = cipher.encrypt(padded_plain_text.encode('utf-8'))
        return base64.b64encode(encrypted_data).decode('utf-8')
    except Exception as e:
        return None
    
def decrypt_aes(encrypted_data, key):
    try:
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted_data = cipher.decrypt(base64.b64decode(encrypted_data))
        print('decrypted_data: ', decrypted_data)
        padding_length = decrypted_data[-1]
        decrypted_data = decrypted_data[:-padding_length]
        return decrypted_data.decode('utf-8')
    except Exception as e:
        return None

class EncryptionFormView(View):
    def post(self, request):
        try:
            # Convert request body to a Python dictionary
            data = json.loads(request.body).get('data')
            print('Received data:', data)  # Check if data is received correctly
            
            # Convert dictionary to JSON string for encryption
            data_str = json.dumps(data)
            
            key = base64.b64decode("bXVzdGJlMTZieXRlc2tleQ==")  # Your key
            encrypted_data = encrypt_aes(data_str, key)  # Encrypt the JSON string
            
            print('Encrypted data:', encrypted_data)
            if encrypted_data is None:
                return JsonResponse({'success': False, 'error': 'Encryption failed'})

            return JsonResponse({'success': True, 'data': encrypted_data})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})



class DecryptionFormView(View):
    
    def post(self, request):
        try:
            # encrypted_data = json.loads(request.body).get('data')
            encrypted_data = json.loads(request.body).get('data')
            print('encrypted_data: ', encrypted_data)
            key = base64.b64decode("bXVzdGJlMTZieXRlc2tleQ==")  # Replace with your Base64 encoded key
            decrypted_data = decrypt_aes(encrypted_data, key)
            print('decrypted_data: ', decrypted_data)
            if decrypted_data is None:
                return JsonResponse({'success': False, 'error': 'Decryption failed'})

            data = json.loads(decrypted_data)

            return JsonResponse({'success': True, 'data': data})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
        
class ProductGenericListCreateAPIView(ListCreateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    
class ProductEncryptionView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'product_encyption_view.html'
    context_object_name = 'products'
    paginate_by = 10
    
    
class ProductEncryptionAPI(LoginRequiredMixin, View):
    
    def get(self, request, *args, **kwargs):
        # Retrieve all products
        products = Product.objects.all()
        
        # Prepare the data manually
        product_list = []
        for product in products:
            product_data = {
                'id': product.id,
                'title': product.title,
                'description': product.description,
                'price': str(product.price),  # Convert Decimal to string
                'status': product.status,
                'created_at': product.created_at.isoformat(),  # ISO format for datetime
                'updated_at': product.updated_at.isoformat(),
                'created_by': product.created_by.email,  # Assuming `created_by` is a User object and you want username
                'category_name': product.category.name,  # Include category name
                'rejection_reason': product.rejection_reason or ''  # Handle empty rejection reason
            }
            product_list.append(product_data)
        
        # Convert the product list to JSON string
        product_json = json.dumps(product_list)
        
        # Encrypt the JSON string
        key = base64.b64decode("bXVzdGJlMTZieXRlc2tleQ==")  # Your key (make sure it has a valid length)
        encrypted_data = encrypt_aes(product_json, key)
        # Return the encrypted data as a JSON response
        return JsonResponse({'data': encrypted_data}, status=200)

    
    
class  ProductList(View):
        
    def get(self, request):
        return render(request, 'product_data_list.html')