from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
<<<<<<< HEAD
from .models import CustemUser

class CustemUserForm(forms.ModelForm):
    class Meta:
        model = CustemUser
        fields = ["username", "email", "avatar", "description"]

        labels = {
            "username": "Никнейм",
            "email": "Почта",
            "avatar": "Аватар пользователя",
            "description": "Описание"
        }
        widgets = {
            "avatar": forms.FileInput() 
        }

        help_texts = {
            "username": "",
            "avatar": ""
        }
    
    def clean_username(self):
        username = self.cleaned_data.get("username")

        if CustemUser.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Пользователь с таким именем уже существует")
        
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get("email")

        if CustemUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует")

        return email
=======
>>>>>>> ec2a4da0743c3521977992317cb1844b7d3a3a10

class AuthenticationForm(forms.Form):
    username = forms.CharField(
        label="Имя пользователя",
        widget=forms.TextInput(attrs={
            "class": "input",
            "placeholder": "Введите ваше имя пользователя"
        })
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            "class": "input",
            "placeholder": "Введите ваш пароль"
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            user = authenticate(
                username=username,
                password=password
            )

            if not user:
                raise forms.ValidationError("Неверный логин или пароль")
            else:
                self.user = user

        return cleaned_data
    
class RegistrationForm(forms.Form):
    email = forms.EmailField(
        label="Электронная почта",
        widget=forms.EmailInput(attrs={
            "class": "input",
            "placeholder": "Введите ваше имя пользователя"
        })
    )
    username = forms.CharField(
        label="Имя пользователя",
        widget=forms.TextInput(attrs={
            "class": "input",
            "placeholder": "Введите ваше имя пользователя"
        })
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            "class": "input",
            "placeholder": "Введите ваш пароль"
        })
    )
    password2 = forms.CharField(
        label="Повторите пароль",
        widget=forms.PasswordInput(attrs={
            "class": "input",
            "placeholder": "Введите ваш пароль еще раз"
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email):
            raise forms.ValidationError("Пользователь с таким email уже существует")
        
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get("username")

        if User.objects.filter(username=username):
            raise forms.ValidationError("Пользователь с таким именем уже существует")
        
        return username
    
    def clean_password(self):
        password = self.cleaned_data.get("password")

        if password.isdigit() or password.isalpha():
            raise forms.ValidationError("Пароль не может состоят только из цифр или букв")

        if not password.strip():
            raise forms.ValidationError("Пароль не может быть пустым")

        if any(c.isspace() for c in password):
            raise forms.ValidationError("Пароль не должен содержать пробелы")

        if len(password) < 8:
            raise forms.ValidationError("Пароль должен содержать минимум 8 символов")

        return password
    
    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Пароли не совпадают")
        
<<<<<<< HEAD
        return cleaned_data
    
=======
        return cleaned_data
>>>>>>> ec2a4da0743c3521977992317cb1844b7d3a3a10
