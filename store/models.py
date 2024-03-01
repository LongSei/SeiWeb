from django.urls import reverse
from category.models import Category
from accounts.models import Account
from django.db import models
import uuid
from django import template
from PIL import Image
class ImageSet(models.Model): 
    set_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self) -> str:
        return str(self.set_id)

    def get_image(self): 
        return ImageModel.objects.filter(image_set=self)
    
class ImageModel(models.Model): 
    image_set = models.ForeignKey(ImageSet, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/')

    def save(self):
        super().save()  
        img = Image.open(self.image.path) 

        if img.height > 400 or img.width > 400:
            new_img = (400, 400)
            img.thumbnail(new_img)
            img.save(self.image.path)  # saving image at the same path

class Product(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    images = models.ForeignKey(ImageSet, on_delete=models.DO_NOTHING)
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    sold = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)    # Khi xóa category thì Product bị xóa
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def delete(self): 
        super().delete()
        ImageSet.objects.get(set_id=self.images.set_id).delete()

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name

class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    images = models.ForeignKey(ImageSet, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def delete(self): 
        super().delete()
        ImageSet.objects.get(set_id=self.images.set_id).delete()
        
    def __str__(self):
        return self.subject
