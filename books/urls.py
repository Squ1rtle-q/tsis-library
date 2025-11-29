from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

from . import views
from .forms import LoginForm
from .views_api import (
    BookListAPIView, BookDetailAPIView,
    AuthorListAPIView, AuthorDetailAPIView,
    CategoryListAPIView, CategoryDetailAPIView,
    BookViewSet,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'api/books', BookViewSet, basename='book')

urlpatterns = [
    path('', views.landing, name='landing'),
    path('library/', views.home, name='home'),

    path('add/', views.add_book, name='add_book'),
    path('edit/<int:pk>/', views.edit_book, name='edit_book'),
    path('delete/<int:pk>/', views.delete_book, name='delete_book'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),

    path('signup/', views.signup_view, name='signup'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='books/login.html',
            authentication_form=LoginForm,
        ),
        name='login',
    ),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),

    path('profile/', views.profile_view, name='profile'),
    path('import-russian-books/', views.import_russian_books, name='import_russian_books'),
    path('users/', views.users_list, name='users_list'),
    path('users/<int:user_id>/', views.user_profile, name='user_profile'),

    path('api/books/', BookListAPIView.as_view(), name='api-books-list'),
    path('api/books/<int:pk>/', BookDetailAPIView.as_view(), name='api-books-detail'),
    path('api/authors/', AuthorListAPIView.as_view(), name='api-authors-list'),
    path('api/authors/<int:pk>/', AuthorDetailAPIView.as_view(), name='api-authors-detail'),
    path('api/categories/', CategoryListAPIView.as_view(), name='api-categories-list'),
    path('api/categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='api-categories-detail'),

    path('', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
