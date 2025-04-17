import pytest

from http import HTTPStatus

from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture


pytestmark = pytest.mark.django_db

# Константы с фикстурами
CLIENT = lazy_fixture('client')
AUTHOR_CLIENT = lazy_fixture('author_client')
NOT_AUTHOR_CLIENT = lazy_fixture('not_author_client')

HOME_URL = lazy_fixture('home_url')
LOGIN_URL = lazy_fixture('login_url')
LOGOUT_URL = lazy_fixture('logout_url')
SIGNUP_URL = lazy_fixture('signup_url')

DETAIL_URL = lazy_fixture('news_detail_url')
EDIT_URL = lazy_fixture('comment_edit_url')
DELETE_URL = lazy_fixture('comment_delete_url')

EDIT_REDIRECT = lazy_fixture('comment_edit_redirect_url')
DELETE_REDIRECT = lazy_fixture('comment_delete_redirect_url')


@pytest.mark.parametrize(
    'url_fixture, client_fixture, expected_status',
    [
        # Публичные страницы
        (HOME_URL, CLIENT, HTTPStatus.OK),
        (LOGIN_URL, CLIENT, HTTPStatus.OK),
        (LOGOUT_URL, CLIENT, HTTPStatus.OK),
        (SIGNUP_URL, CLIENT, HTTPStatus.OK),

        # Детали новости
        (DETAIL_URL,
         CLIENT,
         HTTPStatus.OK
         ),

        # Доступ к редактированию и удалению комментариев
        (EDIT_URL,
         AUTHOR_CLIENT,
         HTTPStatus.OK
         ),
        (DELETE_URL,
         AUTHOR_CLIENT,
         HTTPStatus.OK
         ),
        (EDIT_URL,
         NOT_AUTHOR_CLIENT,
         HTTPStatus.NOT_FOUND
         ),
        (DELETE_URL,
         NOT_AUTHOR_CLIENT,
         HTTPStatus.NOT_FOUND
         ),

        (EDIT_URL, CLIENT, HTTPStatus.FOUND),
        (DELETE_URL, CLIENT, HTTPStatus.FOUND),
    ]
)
def test_status_codes_for_different_pages(
    url_fixture, client_fixture, expected_status
):
    response = client_fixture.get(url_fixture)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture, expected_redirect',
    [
        (EDIT_URL, EDIT_REDIRECT),
        (DELETE_URL, DELETE_REDIRECT),
    ]
)
def test_redirect_for_anonymous_user_on_comment_edit_delete(
    client, url_fixture, expected_redirect
):
    response = client.get(url_fixture)
    assertRedirects(response, expected_redirect)
