from django import forms
from .models import ReviewRating, Product


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']

class StoreFilterForm(forms.Form):
    priceMin = forms.IntegerField()
    priceMax = forms.IntegerField()
    category = forms.CharField()
