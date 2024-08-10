from celery import shared_task
from . models import Category, Product
import string
import random
import time
from django.contrib.auth import get_user_model
User = get_user_model()
import os
import logging
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

@shared_task
def generate_dummy_products_data(no_of_products, user_id):
    print("<>>>>>>>>>>>>>>>>>>>>>>", no_of_products, user_id)
    user = User.objects.get(id=user_id)
    start = time.time()
    for _ in range(10):
        name = ''.join(random.choices(string.ascii_uppercase, k=5))
        category = Category.objects.create(name=name, created_by = user)
        for _ in range(100):
            prod_name = ''.join(random.choices(string.ascii_uppercase, k=5))
            price = random.randrange(1.00, 10000.00)
            product = Product.objects.create(
                category_id = category.id,
                title = prod_name,
                description = f'This Product belongs to Category-{category.name}',
                status = 'draft',
                created_by = user,
                price = price
            )
        duration = (time.time() - start) * 1000


# @shared_task
# def upload_video_task(product_id, video_path):
#     print("<>>>>>>>>>>",product_id, video_path)
#     logger.info(f"Processing video for product {product_id}: {video_path}")
#     product = Product.objects.get(id=product_id)
#     product.video = video_path
#     product.save()


@shared_task
def upload_video_task(product_id, video_data, video_name):
    try:
        product = Product.objects.get(id=product_id)
        video_file = ContentFile(video_data, video_name)
        product.video.save(video_name, video_file, save=True)
        print("<>>>>>>>>>>>>>>>", product)
        logger.info(f"Video successfully processed and saved for product {product_id}: {video_name}")
    except Exception as e:
        logger.error(f"Failed to process video for product {product_id}: {str(e)}")
    