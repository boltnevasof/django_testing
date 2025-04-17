from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db

COMMENT_TEXT = 'Комментарий от автора'
COMMENT_FORM_DATA = {'text': COMMENT_TEXT}


def test_anonymous_user_cannot_post_comment(
        client, news_detail_url, login_url
):
    """Анонимный пользователь не может отправить комментарий."""
    expected_url = f'{login_url}?next={news_detail_url}'
    response = client.post(news_detail_url, data=COMMENT_FORM_DATA)
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_authorized_user_can_post_comment(
        author_client, author, news_detail_url, news
):
    """Авторизованный пользователь может отправить комментарий."""
    expected_redirect = f'{news_detail_url}#comments'
    response = author_client.post(news_detail_url, data=COMMENT_FORM_DATA)
    assertRedirects(response, expected_redirect)

    comment = Comment.objects.get()
    assert comment.text == COMMENT_FORM_DATA['text']
    assert comment.author == author
    assert comment.news == news


def make_bad_comment_data(word):
    return {'text': f'Ты {word}!'}


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_forbidden_word_not_allowed_in_comment(
    author_client, news_detail_url, bad_word
):
    """Комментарий с запрещённым словом не сохраняется."""
    comment_data = make_bad_comment_data(bad_word)
    response = author_client.post(news_detail_url, data=comment_data)
    assertFormError(response, 'form', 'text', WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
    author_client, comment, comment_edit_url, news_detail_comments_url
):
    """Автор комментария может его редактировать."""
    response = author_client.post(comment_edit_url, data=COMMENT_FORM_DATA)
    assertRedirects(response, news_detail_comments_url)

    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == COMMENT_FORM_DATA['text']
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news


def test_author_can_delete_comment(
        author_client, comment, comment_delete_url, news_detail_comments_url
):
    """Автор комментария может его удалить."""
    response = author_client.post(comment_delete_url)
    assertRedirects(response, news_detail_comments_url)
    assert Comment.objects.count() == 0


def test_other_user_cannot_edit_comment(
        not_author_client, comment, comment_edit_url
):
    """Другой пользователь не может редактировать чужой комментарий."""
    response = not_author_client.post(
        comment_edit_url, data=COMMENT_FORM_DATA
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
