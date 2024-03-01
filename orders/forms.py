from django import forms
from .models import Order, Payment


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['Name', 'Phone', 'Email', 'Address', 'Note']

class OrderPaymentForm(forms.Form): 
    paymentQuery = forms.CharField()
