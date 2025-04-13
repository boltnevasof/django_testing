import pytest
from http import HTTPStatus
from news.models import Comment
from news.forms import WARNING, BAD_WORDS
from pytest_django.asserts import assertRedirects, assertFormError

pytestmark = pytest.mark.django_db


def test_anonymous_user_cannot_post_comment(
        client, news_detail_url, login_url
):
    """Анонимный пользователь не может отправить комментарий."""
    comment_data = {'text': 'Анонимный комментарий'}
    response = client.post(news_detail_url, data=comment_data)
    expected_url = f'{login_url}?next={news_detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_authorized_user_can_post_comment(
        author_client, author, news_detail_url
):
    """Авторизованный пользователь может отправить комментарий."""
    comment_data = {'text': 'Комментарий от автора'}
    response = author_client.post(news_detail_url, data=comment_data)
    assertRedirects(response, f'{news_detail_url}#comments')

    comment = Comment.objects.get()
    assert comment.text == comment_data['text']
    assert comment.author == author


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_forbidden_word_not_allowed_in_comment(
    author_client, news_detail_url, bad_word
):
    """Комментарий с запрещённым словом не сохраняется."""
    bad_text = f'Ты {bad_word}!'
    comment_data = {'text': bad_text}
    response = author_client.post(news_detail_url, data=comment_data)
    assertFormError(response, 'form', 'text', WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
        author_client, comment, comment_edit_url, news_detail_url, author, news
):
    """Автор комментария может его редактировать."""
    comment_data = {'text': 'Обновлённый текст'}
    response = author_client.post(comment_edit_url, data=comment_data)
    assertRedirects(response, f'{news_detail_url}#comments')
    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == comment_data['text']
    assert updated_comment.author == author
    assert updated_comment.news == news


def test_author_can_delete_comment(
        author_client, comment, comment_delete_url, news_detail_url
):
    """Автор комментария может его удалить."""
    response = author_client.post(comment_delete_url)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() == 0


def test_other_user_cannot_edit_comment(
        not_author_client, comment, comment_edit_url
):
    """Другой пользователь не может редактировать чужой комментарий."""
    response = not_author_client.post(
        comment_edit_url, data={'text': 'Попытка взлома'}
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
    comment_from_db = Comment.objects.get(pk=comment.pk)
    assert comment_from_db.text == comment.text
    assert comment_from_db.author == comment.author
    assert comment_from_db.news == comment.news
