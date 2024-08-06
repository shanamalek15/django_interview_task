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

    

]

