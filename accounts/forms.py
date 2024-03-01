from django import forms
from django.forms import CharField
from django.forms import widgets
from .models import Account
from store.models import Product 
from category.models import Category
from django.views.generic.edit import FormView

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class MultipleImageUploadForm(forms.Form):
    file_field = MultipleFileField()


class UploadProductsForm(forms.ModelForm): 
    class Meta: 
        model = Product
        fields = ['product_name', 'price', 'stock', 'category', 'description']

class ProfileChangeForm(forms.Form): 
    name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=100)
    phone_number = forms.CharField(max_length=50)

class RegistrationForm(forms.ModelForm):
    name = forms.CharField(max_length=100)

    phone_number = forms.CharField(max_length=50)

    email = forms.EmailField(max_length=50)

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Mật khẩu'
    }))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Nhập lại mật khẩu'
    }))

    class Meta:
        model = Account
        fields = ['name', 'phone_number', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = 'Họ và tên'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Số điện thoại'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                'Mật khẩu không trùng khớp!'
            )
