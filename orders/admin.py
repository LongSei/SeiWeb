from django.contrib import admin
from .models import Order, OrderProduct, Payment

class PaymentAdmin(admin.ModelAdmin): 
    list_display = ('payment_id', 'user', 'status', 'amount_paid')

class OrderProductAdmin(admin.ModelAdmin): 
    list_display = ('product', 'quantity', 'payment')

class OrderAdmin(admin.ModelAdmin): 
    list_display = ('user', 'payment', 'created_at', 'status')
    
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)
