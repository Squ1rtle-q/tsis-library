from django.core.paginator import Paginator
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .models import Book, Category, Profile, Author
from .forms import BookForm, SignUpForm, ProfileForm, LoginForm
import requests


def users_list(request):
    users = User.objects.all()
    return render(request, 'books/users_list.html', {'users': users})


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
    else:
        form = ProfileForm(instance=profile)

    user_books = Book.objects.filter(owner=request.user, is_external=False)

    context = {
        'form': form,
        'profile': profile,
        'user_books': user_books,
    }
    return render(request, 'books/profile.html', context)


@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.owner = request.user
            book.is_external = False
            book.save()
            messages.success(request, 'Книга добавлена успешно!')
            return redirect('home')
    else:
        form = BookForm()

    return render(request, 'books/add_book.html', {'form': form})


@login_required
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if not request.user.is_superuser:
        if book.is_external or book.owner != request.user:
            messages.error(request, 'У вас нет прав редактировать эту книгу.')
            return redirect('home')

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Книга обновлена!')
            return redirect('home')
    else:
        form = BookForm(instance=book)

    return render(request, 'books/edit_book.html', {'form': form, 'book': book})


@login_required
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if not request.user.is_superuser:
        if book.is_external or book.owner != request.user:
            messages.error(request, 'У вас нет прав удалять эту книгу.')
            return redirect('home')

    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Книга удалена!')
        return redirect('home')

    return render(request, 'books/delete_book.html', {'book': book})

def landing(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'books/landing.html')

def home(request):
    tab = request.GET.get('tab', 'local')
    query = request.GET.get('q', '')
    cat_id = request.GET.get('category', '')
    author_name = request.GET.get('author', '')

    categories = Category.objects.all()
    authors = Author.objects.all()

    local_books = Book.objects.filter(is_external=False)
    external_books = Book.objects.filter(is_external=True)

    current_category = None
    if cat_id:
        current_category = Category.objects.filter(id=cat_id).first()

    if tab == 'local':
        books_qs = local_books
    else:
        books_qs = external_books

    if query:
        books_qs = books_qs.filter(title__icontains=query)

    if cat_id:
        books_qs = books_qs.filter(category_id=cat_id)

    if author_name:
        books_qs = books_qs.filter(author__icontains=author_name)

    page_obj = None
    if tab == 'external':
        paginator = Paginator(books_qs, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        books_qs = page_obj

    context = {
        'active_tab': tab,
        'books': books_qs,
        'page_obj': page_obj,
        'categories': categories,
        'authors': authors,
        'query': query,
        'cat_id': cat_id,
        'author_name': author_name,
        'current_category': current_category,
    }
    return render(request, 'books/home.html', context)


@login_required
def import_russian_books(request):
    russian_authors = [
        'Лев Толстой',
        'Фёдор Достоевский',
        'Александр Пушкин',
        'Антон Чехов',
        'Николай Гоголь',
    ]

    imported_count = 0

    for author_name in russian_authors:
        params = {
            'author': author_name,
            'language': 'rus',
            'limit': 100,
        }

        try:
            resp = requests.get('https://openlibrary.org/search.json', params=params, timeout=5)
            if resp.status_code != 200:
                continue

            data = resp.json()

            for doc in data.get('docs', []):
                title = doc.get('title', '')
                authors_list = doc.get('author_name', [])
                ext_author = authors_list[0] if authors_list else author_name

                subjects = doc.get('subject', []) or doc.get('subject_facet', []) or []
                category_name = 'Без категории'
                for s in subjects:
                    if any('а' <= ch.lower() <= 'я' for ch in s):
                        category_name = s
                        break
                if category_name == 'Без категории' and subjects:
                    category_name = subjects[0]

                if not any('а' <= ch.lower() <= 'я' for ch in title):
                    continue

                author_obj, _ = Author.objects.get_or_create(name=ext_author)
                category_obj, _ = Category.objects.get_or_create(name=category_name)

                if Book.objects.filter(title=title, author=ext_author).exists():
                    continue

                work_key = doc.get('key')
                info_url = None
                buy_url = None
                description = 'Описание пока не задано'

                if work_key:
                    info_url = f'https://openlibrary.org{work_key}'

                    try:
                        work_resp = requests.get(f'https://openlibrary.org{work_key}.json', timeout=5)
                        if work_resp.status_code == 200:
                            work_data = work_resp.json()
                            desc_field = work_data.get('description')
                            if isinstance(desc_field, dict):
                                description = desc_field.get('value', description)
                            elif isinstance(desc_field, str):
                                description = desc_field
                    except requests.RequestException:
                        pass

                    search_title = requests.utils.quote(title)
                    buy_url = f'https://www.google.com/search?q=купить+книгу+{search_title}'


                book = Book.objects.create(
                    title=title,
                    author=ext_author,
                    description=description,
                    category=category_obj,
                    is_external=True,
                    info_url=info_url,
                    buy_url=buy_url,
                )

                cover_id = doc.get('cover_i')
                if cover_id:
                    cover_url = f'https://covers.openlibrary.org/b/id/{cover_id}-L.jpg'
                    try:
                        img_resp = requests.get(cover_url, timeout=5)
                        if img_resp.status_code == 200:
                            filename = slugify(title)[:40] or f'book-{book.id}'
                            book.image.save(
                                f'{filename}.jpg',
                                ContentFile(img_resp.content),
                                save=True,
                            )
                    except requests.RequestException:
                        pass

                imported_count += 1

        except requests.RequestException:
            continue

    messages.success(request, f'Импортировано книг: {imported_count}')
    return redirect('home')


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'books/book_detail.html', {'book': book})


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'books/signup.html', {'form': form})


def user_profile(request, user_id):
    user_obj = get_object_or_404(User, pk=user_id)
    user_books = Book.objects.filter(owner=user_obj, is_external=False)
    return render(request, 'books/user_profile.html', {
        'profile_user': user_obj,
        'user_books': user_books,
    })
