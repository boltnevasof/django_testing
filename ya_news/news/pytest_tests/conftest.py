import pytest
from django.test.client import Client
from news.models import News, Comment

from datetime import timedelta
from django.utils import timezone


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Новость',
        text='Текст новости',
    )


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def news_bulk():
    now = timezone.now()
    for i in range(15):  # Создаём больше 10, чтобы проверить ограничение
        News.objects.create(
            title=f'Новость {i}',
            text='Текст',
            date=now - timedelta(days=i)
        )


@pytest.fixture
def comments_bulk(news, author):
    now = timezone.now()
    for i in range(3):
        Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {i}',
            created=now + timedelta(minutes=i)
        )
