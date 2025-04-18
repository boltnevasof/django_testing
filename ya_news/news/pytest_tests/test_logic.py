from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


COMMENT_FORM_DATA = {'text': 'Комментарий от автора'}
BAD_COMMENT_TEMPLATE = 'Ты {}!'
BAD_COMMENTS = [
    {'text': BAD_COMMENT_TEMPLATE.format(word)} for word in BAD_WORDS
]


def test_anonymous_user_cannot_post_comment(
        client, news_detail_url, login_url, comment_post_redirect_url
):
    """Анонимный пользователь не может отправить комментарий."""
    response = client.post(news_detail_url, data=COMMENT_FORM_DATA)
    assertRedirects(response, comment_post_redirect_url)
    assert Comment.objects.count() == 0


def test_authorized_user_can_post_comment(
        author_client, author, news_detail_url, news, news_detail_comments_url
):
    """Авторизованный пользователь может отправить комментарий."""
    response = author_client.post(news_detail_url, data=COMMENT_FORM_DATA)
    assertRedirects(response, news_detail_comments_url)

    comment = Comment.objects.get()
    assert comment.text == COMMENT_FORM_DATA['text']
    assert comment.author == author
    assert comment.news == news


@pytest.mark.parametrize('bad_comment_data', BAD_COMMENTS)
def test_forbidden_word_not_allowed_in_comment(
        author_client, news_detail_url, bad_comment_data
):
    """Комментарий с запрещённым словом не сохраняется."""
    response = author_client.post(news_detail_url, data=bad_comment_data)
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
