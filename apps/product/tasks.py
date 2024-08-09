from celery import shared_task
from . models import Category, Product
import string
import random
import time
from django.contrib.auth import get_user_model
User = get_user_model()
import os


@shared_task
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
    print("<>>>>>>>>>>",product_id, video_path)
    product = Product.objects.get(id=product_id)
    product.video = video_path
    product.save()
    
    
# @shared_task
# def upload_video_task(product_id, video_path):
    # Path to the temporary video file
    temp_video_path = video_path
    final_video_path = os.path.join('media', 'videos', os.path.basename(video_path))

    # Perform any video processing here (e.g., transcoding, compression)
    # For demonstration, we're just moving the file
    if os.path.exists(temp_video_path):
        # Move the processed video to the final location
        os.rename(temp_video_path, final_video_path)

        # Update the product record with the final video path and mark as complete
        product = Product.objects.get(id=product_id)
        product.video = final_video_path
        product.status = 'approved'
        product.save()

        # Clean up (e.g., delete temp files)
        # No additional cleanup needed here as temp file is moved to final location
    else:
        print("Temp video file does not exist.")