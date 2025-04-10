import pytest
from http import HTTPStatus
from django.urls import reverse
from news.models import Comment
from news.forms import WARNING
from pytest_django.asserts import assertRedirects, assertFormError


@pytest.mark.django_db
def test_anonymous_user_cannot_post_comment(client, news):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=[news.pk])
    response = client.post(url, data={'text': 'Анонимный комментарий'})
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_authorized_user_can_post_comment(author_client, author, news):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=[news.pk])
    response = author_client.post(url, data={'text': 'Комментарий от автора'})
    assertRedirects(response, f'{url}#comments')
    comment = Comment.objects.get()
    assert comment.text == 'Комментарий от автора'
    assert comment.author == author
    assert comment.news == news


@pytest.mark.django_db
def test_forbidden_word_not_allowed_in_comment(author_client, news):
    """Комментарий с запрещённым словом не сохраняется."""
    url = reverse('news:detail', args=[news.pk])
    bad_text = 'Ты редиска!'
    response = author_client.post(url, data={'text': bad_text})
    assertFormError(response, 'form', 'text', WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment):
    """Автор комментария может его редактировать."""
    url = reverse('news:edit', args=[comment.pk])
    new_text = 'Обновлённый текст'
    response = author_client.post(url, data={'text': new_text})
    assertRedirects(response, reverse('news:detail', args=[comment.news.pk]) + '#comments')
    comment.refresh_from_db()
    assert comment.text == new_text


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    """Автор комментария может его удалить."""
    url = reverse('news:delete', args=[comment.pk])
    response = author_client.post(url)
    assertRedirects(response, reverse('news:detail', args=[comment.news.pk]) + '#comments')
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_other_user_cannot_edit_comment(not_author_client, comment):
    """Другой пользователь не может редактировать чужой комментарий."""
    url = reverse('news:edit', args=[comment.pk])
    response = not_author_client.post(url, data={'text': 'Попытка взлома'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Проверим, что текст остался прежним
    comment_from_db = Comment.objects.get(pk=comment.pk)
    assert comment.text == comment_from_db.text


@pytest.mark.django_db
def test_other_user_cannot_delete_comment(not_author_client, comment):
    """Другой пользователь не может удалить чужой комментарий."""
    url = reverse('news:delete', args=[comment.pk])
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.pk).exists()
