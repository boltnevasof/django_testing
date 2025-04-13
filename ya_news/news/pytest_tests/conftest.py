from datetime import timedelta

import pytest
from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News
from django.conf import settings
from django.urls import reverse


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def comment_edit_url(comment):
    return reverse('news:edit', args=[comment.pk])


@pytest.fixture
def comment_delete_url(comment):
    return reverse('news:delete', args=[comment.pk])


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=[news.pk])


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
    news_list = []
    now = timezone.now()
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 5):
        news_list.append(News(
            title=f'Новость {i}',
            text='Текст',
            date=now - timedelta(days=i)
        ))
    News.objects.bulk_create(news_list)


@pytest.fixture
def comments_bulk(news, author):
    for i in range(3):
        Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {i}',
        )


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')
