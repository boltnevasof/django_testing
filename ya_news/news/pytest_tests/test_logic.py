from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db

COMMENT_TEXT = 'Комментарий от автора'
UPDATED_TEXT = 'Обновлённый текст'
ANONYMOUS_COMMENT = {'text': 'Анонимный комментарий'}
AUTHOR_COMMENT = {'text': COMMENT_TEXT}
UPDATED_COMMENT = {'text': UPDATED_TEXT}


def test_anonymous_user_cannot_post_comment(
        client, news_detail_url, login_url
):
    """Анонимный пользователь не может отправить комментарий."""
    expected_url = f'{login_url}?next={news_detail_url}'
    response = client.post(news_detail_url, data=ANONYMOUS_COMMENT)
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_authorized_user_can_post_comment(
        author_client, author, news_detail_url, news
):
    """Авторизованный пользователь может отправить комментарий."""
    expected_redirect = f'{news_detail_url}#comments'
    response = author_client.post(news_detail_url, data=AUTHOR_COMMENT)
    assertRedirects(response, expected_redirect)

    comment = Comment.objects.get()
    assert comment.text == AUTHOR_COMMENT['text']
    assert comment.author == author
    assert comment.news == news


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_forbidden_word_not_allowed_in_comment(
    author_client, news_detail_url, bad_word
):
    """Комментарий с запрещённым словом не сохраняется."""
    comment_data = {'text': f'Ты {bad_word}!'}
    response = author_client.post(news_detail_url, data=comment_data)
    assertFormError(response, 'form', 'text', WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
        author_client, comment, comment_edit_url, news_detail_url, author, news
):
    """Автор комментария может его редактировать."""
    expected_redirect = f'{news_detail_url}#comments'
    response = author_client.post(comment_edit_url, data=UPDATED_COMMENT)
    assertRedirects(response, expected_redirect)
    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == UPDATED_COMMENT['text']
    assert updated_comment.author == author
    assert updated_comment.news == news


def test_author_can_delete_comment(
        author_client, comment, comment_delete_url, news_detail_url
):
    """Автор комментария может его удалить."""
    expected_redirect = f'{news_detail_url}#comments'
    response = author_client.post(comment_delete_url)
    assertRedirects(response, expected_redirect)
    assert Comment.objects.count() == 0


def test_other_user_cannot_edit_comment(
        not_author_client, comment, comment_edit_url
):
    """Другой пользователь не может редактировать чужой комментарий."""
    response = not_author_client.post(
        comment_edit_url, data=UPDATED_COMMENT
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(pk=comment.pk)
    assert comment_from_db.text == comment.text
    assert comment_from_db.author == comment.author
    assert comment_from_db.news == comment.news


def test_other_user_cannot_delete_comment(
    not_author_client, comment, comment_delete_url
):
    """Другой пользователь не может удалить чужой комментарий."""
    response = not_author_client.post(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.pk).exists()

    comment_from_db = Comment.objects.get(pk=comment.pk)
    assert comment_from_db.text == comment.text
    assert comment_from_db.author == comment.author
    assert comment_from_db.news == comment.news
