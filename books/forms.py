from django import forms
from .models import Book, Profile
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(
        label='Аватар',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Profile
        fields = ['avatar']


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        label='Имя пользователя',
        help_text='До 150 символов. Только буквы, цифры и символы @/./+/-/_.',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Email',
        max_length=254,
        help_text='Обязательное поле. Укажите действующий email.',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Пароль должен содержать минимум 8 символов и не быть слишком простым.'
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Введите тот же пароль ещё раз для проверки.'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'description', 'category', 'image']
        labels = {
            'title': 'Название',
            'author': 'Автор',
            'description': 'Описание',
            'category': 'Категория',
            'image': 'Обложка',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
