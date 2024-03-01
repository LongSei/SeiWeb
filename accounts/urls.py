from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),

    path('storeHistory/', views.storeHistory, name='storeHistory'),
    path('uploadProducts/', views.uploadProducts, name="uploadProducts"),
    path('uploadProduct/<int:product_id>', views.uploadProducts, name='editProduct'),
    path('deleteProduct/<int:product_id>', views.deleteProducts, name='deleteProduct'),
    path('profile/', views.profile, name='profile'),
    path('orderHistory/', views.orderHistory, name='orderHistory'),
    path('soldHistory/', views.soldHistory, name="soldHistory"),
    path('editOrder/<str:order_number>/<str:method>', views.editOrder, name="editOrder"),
    path('', views.orderHistory, name='orderHistory'),

    path('change_profile/<uidb64>/<token>/<email>/<phone_number>', views.change_profile, name='change_profile'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('reset_password_validate/<uidb64>/<token>', views.reset_password_validate, name='reset_password_validate'),
    path('reset_password/', views.reset_password, name='reset_password')
]
