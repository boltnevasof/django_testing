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
            (self.not_author_client, self.DETAIL_URL, HTTPStatus.NOT_FOUND),
            (self.not_author_client, self.EDIT_URL, HTTPStatus.NOT_FOUND),
            (self.not_author_client, self.DELETE_URL, HTTPStatus.NOT_FOUND),

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
        protected_redirects = [
            (self.LIST_URL, self.LOGIN_LIST_REDIRECT),
            (self.SUCCESS_URL, self.LOGIN_SUCCESS_REDIRECT),
            (self.ADD_URL, self.LOGIN_ADD_REDIRECT),
            (self.DETAIL_URL, self.LOGIN_DETAIL_REDIRECT),
            (self.EDIT_URL, self.LOGIN_EDIT_REDIRECT),
            (self.DELETE_URL, self.LOGIN_DELETE_REDIRECT),
        ]
        for url, expected_redirect in protected_redirects:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, expected_redirect)
