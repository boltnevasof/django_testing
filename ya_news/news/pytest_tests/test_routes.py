import pytest
from http import HTTPStatus
from pytest_lazyfixture import lazy_fixture
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_fixture, client_fixture, expected_status',
    [
        # Публичные страницы
        (lazy_fixture('home_url'), lazy_fixture('client'), HTTPStatus.OK),
        (lazy_fixture('login_url'), lazy_fixture('client'), HTTPStatus.OK),
        (lazy_fixture('logout_url'), lazy_fixture('client'), HTTPStatus.OK),
        (lazy_fixture('signup_url'), lazy_fixture('client'), HTTPStatus.OK),

        # Детали новости
        (lazy_fixture('news_detail_url'),
         lazy_fixture('client'),
         HTTPStatus.OK
         ),

        # Доступ к редактированию и удалению комментариев
        (lazy_fixture('comment_edit_url'),
         lazy_fixture('author_client'),
         HTTPStatus.OK
         ),
        (lazy_fixture('comment_delete_url'),
         lazy_fixture('author_client'),
         HTTPStatus.OK
         ),
        (lazy_fixture('comment_edit_url'),
         lazy_fixture('not_author_client'),
         HTTPStatus.NOT_FOUND
         ),
        (lazy_fixture('comment_delete_url'),
         lazy_fixture('not_author_client'),
         HTTPStatus.NOT_FOUND
         ),
    ]
)
def test_status_codes_for_different_pages(
    url_fixture, client_fixture, expected_status
):
    response = client_fixture.get(url_fixture)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture',
    (lazy_fixture('comment_edit_url'), lazy_fixture('comment_delete_url'))
)
def test_redirect_for_anonymous_user_on_comment_edit_delete(
    client, login_url, url_fixture
):
    expected_redirect = f'{login_url}?next={url_fixture}'
    response = client.get(url_fixture)
    assertRedirects(response, expected_redirect)
