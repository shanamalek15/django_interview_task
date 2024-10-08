from django.urls import path, include
from .views import *
app_name = 'product'
urlpatterns = [
    # Category URLs
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/update/', CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'),
    path('categories/detail/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),


    # Product URLs
    path('', ProductListView.as_view(), name='product-list'),
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('update/<int:pk>/', ProductUpdateView.as_view(), name='product-update'),
    path('delete/<int:pk>/', ProductDeleteView.as_view(), name='product-delete'),
    path('detail/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('product-approval/<int:pk>/', ProductApprovalUpdateView.as_view(), name='product-approval'),
    path('export-products/', ExportProductsView.as_view(), name='export-products'),
    path('generate-products/', GenerateDummyProductsView.as_view(), name='generate-dummy-products'),
    path('product/approval/<int:pk>', ProductApprovalView.as_view(), name='product-approval'),

    path('encryption-form/', EncryptionView.as_view(), name='encryption-form'),
    path('encryption/', EncryptionFormView.as_view(), name='encryption'),
    path('decryption/', DecryptionFormView.as_view(), name='decryption'),
    path('product-api/', ProductGenericListCreateAPIView.as_view(), name='prodcut-api'),
    path('product-encryption-view/', ProductEncryptionView.as_view(), name='product-encryption-view'),
    
    path('product-encryption-api/', ProductEncryptionAPI.as_view(), name='product-encryption-api'),
    path('list-products/', ProductList.as_view(), name='product-list-view'),  # This renders the HTML template
]

