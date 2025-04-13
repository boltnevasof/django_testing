from http import HTTPStatus
from django.urls import reverse

from .test_urls import (
    home_url, login_url, logout_url, signup_url,
    detail_url, edit_url, delete_url
)
from .test_base import BaseTestCase


class TestRoutes(BaseTestCase):
    def test_all_status_codes(self):
        """Контроль всех кодов возврата для разных клиентов."""
        cases = [
            # Публичные страницы
            (self.client, home_url(), HTTPStatus.OK),
            (self.client, login_url(), HTTPStatus.OK),
            (self.client, logout_url(), HTTPStatus.OK),
            (self.client, signup_url(), HTTPStatus.OK),

            # Защищённые — для автора
            (self.authorized_client, reverse('notes:list'), HTTPStatus.OK),
            (self.authorized_client, reverse('notes:success'), HTTPStatus.OK),
            (self.authorized_client, reverse('notes:add'), HTTPStatus.OK),
            (self.authorized_client, detail_url(), HTTPStatus.OK),
            (self.authorized_client, edit_url(), HTTPStatus.OK),
            (self.authorized_client, delete_url(), HTTPStatus.OK),

            # Защищённые — для другого пользователя
            (self.other_client, detail_url(), HTTPStatus.NOT_FOUND),
            (self.other_client, edit_url(), HTTPStatus.NOT_FOUND),
            (self.other_client, delete_url(), HTTPStatus.NOT_FOUND),
        ]
        for client, url, expected in cases:
            with self.subTest(url=url):
                self.assertEqual(client.get(url).status_code, expected)

    def test_redirects_for_anonymous(self):
        """Аноним перенаправляется на логин со всех защищённых страниц."""
        login_url = reverse('users:login')
        protected_urls = [
            reverse('notes:list'),
            reverse('notes:success'),
            reverse('notes:add'),
            detail_url(),
            edit_url(),
            delete_url(),
        ]
        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertTrue(response.url.startswith(f'{login_url}?next='))
