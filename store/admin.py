from django.contrib import admin
from .models import Product, ReviewRating, ImageModel


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'sold', 'category', 'created_date', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}

class ImageModelAdmin(admin.ModelAdmin): 
    list_display = ('image_set', 'image')

class ReviewRatingAdmin(admin.ModelAdmin): 
    list_display = ('subject', 'product', 'user', 'rating')

admin.site.register(ImageModel, ImageModelAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ReviewRating, ReviewRatingAdmin)
