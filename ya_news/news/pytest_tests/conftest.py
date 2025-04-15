from datetime import timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


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
    now = timezone.now()
    news_list = [
        News(
            title=f'Новость {i}',
            text='Текст',
            date=now - timedelta(days=i)
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 5)
    ]
    News.objects.bulk_create(news_list)


@pytest.fixture
def comments_bulk(news, author):
    now = timezone.now()
    comments = [
        Comment(
            news=news,
            author=author,
            text=f'Комментарий {i}',
            created=now + timedelta(minutes=i)
        )
        for i in range(3)
    ]
    Comment.objects.bulk_create(comments)


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def comment_edit_redirect_url(login_url, comment_edit_url):
    return f'{login_url}?next={comment_edit_url}'


@pytest.fixture
def comment_delete_redirect_url(login_url, comment_delete_url):
    return f'{login_url}?next={comment_delete_url}'
