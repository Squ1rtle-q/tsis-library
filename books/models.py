from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/default.jpg',
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.user.username


class Author(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="books",
    )
    image = models.ImageField(upload_to='book_covers/', blank=True, null=True)

    info_url = models.URLField(max_length=500, null=True, blank=True)
    buy_url = models.URLField(max_length=500, null=True, blank=True)

    is_external = models.BooleanField(default=False)
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books',
    )

    def __str__(self):
        return self.title
