import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_news_count_limit_on_home_page(client, news_bulk):
    """На главной странице отображается не более 10 новостей."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) <= 10


@pytest.mark.django_db
def test_comments_sorted_by_date(client, news, comments_bulk):
    url = reverse('news:detail', args=[news.pk])
    response = client.get(url)
    comments = list(response.context['object'].comment_set.all())

    for i in range(1, len(comments)):
        assert comments[i - 1].created <= comments[i].created


@pytest.mark.django_db
def test_comments_order_on_news_detail(client, news, comments_bulk):
    url = reverse('news:detail', args=[news.pk])
    response = client.get(url)

    # Получаем все комментарии этой новости
    comments = list(response.context['object'].comment_set.all())

    # Проверяем, что они уже идут по порядку (от старых к новым)
    for i in range(1, len(comments)):
        assert comments[i - 1].created <= comments[i].created


@pytest.mark.django_db
def test_comment_form_for_authorized_user(author_client, news):
    """Авторизованному пользователю доступна форма отправки комментария."""
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.get(url)
    assert 'form' in response.context


@pytest.mark.django_db
def test_comment_form_for_anonymous_user(client, news):
    """Анонимному пользователю форма отправки комментария недоступна."""
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert 'form' not in response.context
