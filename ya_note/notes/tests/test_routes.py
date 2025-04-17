from http import HTTPStatus

from .test_base import BaseTestCase


class TestRoutes(BaseTestCase):
    def test_all_status_codes(self):
        """Контроль всех кодов возврата для разных клиентов."""
        cases = [
            # Публичные страницы
            (self.client, self.HOME_URL, HTTPStatus.OK),
            (self.client, self.LOGIN_URL, HTTPStatus.OK),
            (self.client, self.LOGOUT_URL, HTTPStatus.OK),
            (self.client, self.SIGNUP_URL, HTTPStatus.OK),

            # Защищённые для автора
            (self.authorized_client, self.LIST_URL, HTTPStatus.OK),
            (self.authorized_client, self.SUCCESS_URL, HTTPStatus.OK),
            (self.authorized_client, self.ADD_URL, HTTPStatus.OK),
            (self.authorized_client, self.DETAIL_URL, HTTPStatus.OK),
            (self.authorized_client, self.EDIT_URL, HTTPStatus.OK),
            (self.authorized_client, self.DELETE_URL, HTTPStatus.OK),

            # Защищённые для другого пользователя
            (self.other_client, self.DETAIL_URL, HTTPStatus.NOT_FOUND),
            (self.other_client, self.EDIT_URL, HTTPStatus.NOT_FOUND),
            (self.other_client, self.DELETE_URL, HTTPStatus.NOT_FOUND),

            # Аноним и защищённые страницы (ожидаем редирект)
            (self.client, self.LIST_URL, HTTPStatus.FOUND),
            (self.client, self.SUCCESS_URL, HTTPStatus.FOUND),
            (self.client, self.ADD_URL, HTTPStatus.FOUND),
            (self.client, self.DETAIL_URL, HTTPStatus.FOUND),
            (self.client, self.EDIT_URL, HTTPStatus.FOUND),
            (self.client, self.DELETE_URL, HTTPStatus.FOUND),
        ]
        for client, url, expected_status in cases:
            with self.subTest(client=client, url=url, status=expected_status):
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirects_for_anonymous(self):
        """Аноним перенаправляется на логин со всех защищённых страниц."""
        for url, expected_redirect in self.LOGIN_REDIRECTS:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, expected_redirect)
