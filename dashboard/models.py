from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from django.contrib import admin
from django.utils.crypto import get_random_string

class Profile(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    follows = models.ManyToManyField(
        "self",
        related_name="followed_by",
        symmetrical=False,
        blank=True
    )
    avatar = models.ImageField(upload_to="avatar/", blank=True)
    def saveImage(self):
        super().save()
        img = Image.open(self.avatar.path) 
        if img.height > 300 or img.width > 300:
            new_img = (300, 300)
            img.thumbnail(new_img)
            img.save(self.avatar.path) 

    def __str__(self):
        return (
            f"{self.user.username}"
            f"{self.user.password}"
            f"{self.user.email}"
        )
    
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created == True:
        user_profile = Profile(user=instance)
        user_profile.save()
        user_profile.follows.add(instance.profile)
        user_profile.save()

class Blog(models.Model):
    user = models.ForeignKey(
        User, 
        related_name="blogs", 
        on_delete=models.DO_NOTHING
    )
    header = models.CharField(max_length=200)
    body = models.CharField(max_length=5000)
    created_at = models.DateTimeField()
    def __str__(self):
        return (
            f"{self.user}"
            f"({self.header[:30]}):"
        )

admin.site.register(Profile)
