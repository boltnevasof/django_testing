from http import HTTPStatus

from .test_base import BaseTestCase
from .test_urls import (
    HOME_URL, LOGIN_URL, LOGOUT_URL, SIGNUP_URL, LIST_URL,
    SUCCESS_URL, ADD_URL, DETAIL_URL, EDIT_URL, DELETE_URL
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

            # Защищённые — для автора
            (self.authorized_client, LIST_URL, HTTPStatus.OK),
            (self.authorized_client, SUCCESS_URL, HTTPStatus.OK),
            (self.authorized_client, ADD_URL, HTTPStatus.OK),
            (self.authorized_client, DETAIL_URL, HTTPStatus.OK),
            (self.authorized_client, EDIT_URL, HTTPStatus.OK),
            (self.authorized_client, DELETE_URL, HTTPStatus.OK),

            # Защищённые — для другого пользователя
            (self.other_client, DETAIL_URL, HTTPStatus.NOT_FOUND),
            (self.other_client, EDIT_URL, HTTPStatus.NOT_FOUND),
            (self.other_client, DELETE_URL, HTTPStatus.NOT_FOUND),

            # Аноним и защищённые страницы (ожидаем редирект)
            (self.client, LIST_URL, HTTPStatus.FOUND),
            (self.client, SUCCESS_URL, HTTPStatus.FOUND),
            (self.client, ADD_URL, HTTPStatus.FOUND),
            (self.client, DETAIL_URL, HTTPStatus.FOUND),
            (self.client, EDIT_URL, HTTPStatus.FOUND),
            (self.client, DELETE_URL, HTTPStatus.FOUND),
        ]
        for client, url, expected_status in cases:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirects_for_anonymous(self):
        """Аноним перенаправляется на логин со всех защищённых страниц."""
        login = LOGIN_URL
        protected_urls = [
            LIST_URL, SUCCESS_URL, ADD_URL, DETAIL_URL, EDIT_URL, DELETE_URL
        ]
        for url in protected_urls:
            with self.subTest(url=url):
                expected_redirect = f'{login}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_redirect)
