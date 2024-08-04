from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.contrib.auth import get_user_model
User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        # verbose_name = "Catagory"
        verbose_name_plural = "Catagories"

    def __str__(self) :
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    upload_status = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=40, choices=upload_status, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.FileField(upload_to='videos/', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Products"

    def __str__(self) :
        return self.title