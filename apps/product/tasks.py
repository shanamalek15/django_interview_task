from celery import shared_task
from . models import Category, Product
import string
import random
import time
from django.contrib.auth import get_user_model
User = get_user_model()

@shared_task
# @timer
def generate_dummy_products_data(no_of_products, user_id):
    print("<>>>>>>>>>>>>>>>>>>>>>>", no_of_products, user_id)
    user = User.objects.get(id=user_id)
    print('user: ', user)

    start = time.time()
    print('start: ', start)
    for _ in range(10):
        name = ''.join(random.choices(string.ascii_uppercase, k=5))
        category = Category.objects.create(name=name, created_by = user)
        for _ in range(100):
            prod_name = ''.join(random.choices(string.ascii_uppercase, k=5))
            price = random.randrange(1.00, 10000.00)
            print('price: ', price)
            product = Product.objects.create(
                category_id = category.id,
                title = prod_name,
                description = f'This Product belongs to Category-{category.name}',
                status = 'draft',
                created_by = user,
                price = price
            )
            print('name: ', product)
        duration = (time.time() - start) * 1000
        print('duration: ', duration)


@shared_task
def upload_video_task(product_id, video_path):
    product = Product.objects.get(id=product_id)
    product.video = video_path
    product.save()