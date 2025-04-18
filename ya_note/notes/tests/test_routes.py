from http import HTTPStatus

from .test_base import (
    BaseTestCase,
    ADD_URL, LIST_URL, EDIT_URL, DELETE_URL,
    LOGIN_URL, LOGOUT_URL, SIGNUP_URL,
    HOME_URL, SUCCESS_URL,
    LOGIN_LIST_REDIRECT, LOGIN_SUCCESS_REDIRECT,
    LOGIN_ADD_REDIRECT, LOGIN_DETAIL_REDIRECT,
    LOGIN_EDIT_REDIRECT, LOGIN_DELETE_REDIRECT, DETAIL_URL
)


class TestRoutes(BaseTestCase):
    def test_all_status_codes(self):
        """Контроль всех кодов возврата для разных клиентов."""
        cases = [
            # Публичные страницы
            (self.client, HOME_URL, HTTPStatus.OK),
            (self.client, LOGIN_URL, HTTPStatus.OK),
            (self.client, LOGOUT_URL, HTTPStatus.OK),
            (self.client, SIGNUP_URL, HTTPStatus.OK),

            # Защищённые для автора
            (self.authorized_client, LIST_URL, HTTPStatus.OK),
            (self.authorized_client, SUCCESS_URL, HTTPStatus.OK),
            (self.authorized_client, ADD_URL, HTTPStatus.OK),
            (self.authorized_client, DETAIL_URL, HTTPStatus.OK),
            (self.authorized_client, EDIT_URL, HTTPStatus.OK),
            (self.authorized_client, DELETE_URL, HTTPStatus.OK),

            # Защищённые для другого пользователя
            (self.not_author_client, DETAIL_URL, HTTPStatus.NOT_FOUND),
            (self.not_author_client, EDIT_URL, HTTPStatus.NOT_FOUND),
            (self.not_author_client, DELETE_URL, HTTPStatus.NOT_FOUND),

            # Аноним и защищённые страницы (ожидаем редирект)
            (self.client, LIST_URL, HTTPStatus.FOUND),
            (self.client, SUCCESS_URL, HTTPStatus.FOUND),
            (self.client, ADD_URL, HTTPStatus.FOUND),
            (self.client, DETAIL_URL, HTTPStatus.FOUND),
            (self.client, EDIT_URL, HTTPStatus.FOUND),
            (self.client, DELETE_URL, HTTPStatus.FOUND),
        ]

        for client, url, expected_status in cases:
            with self.subTest(client=client, url=url, status=expected_status):
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirects_for_anonymous(self):
        """Аноним перенаправляется на логин со всех защищённых страниц."""
        protected_redirects = [
            (LIST_URL, LOGIN_LIST_REDIRECT),
            (SUCCESS_URL, LOGIN_SUCCESS_REDIRECT),
            (ADD_URL, LOGIN_ADD_REDIRECT),
            (DETAIL_URL, LOGIN_DETAIL_REDIRECT),
            (EDIT_URL, LOGIN_EDIT_REDIRECT),
            (DELETE_URL, LOGIN_DELETE_REDIRECT),
        ]
        for url, expected_redirect in protected_redirects:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, expected_redirect)
