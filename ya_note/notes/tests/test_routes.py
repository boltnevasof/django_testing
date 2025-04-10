from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author',
            password='pass'
        )
        cls.other_user = User.objects.create_user(
            username='other',
            password='pass'
        )

        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст',
            author=cls.author,
            slug='test-slug'
        )

        cls.urls_for_authorized = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        )

        cls.urls_for_detail_access = (
            ('notes:detail', (cls.note.slug,)),
            ('notes:edit', (cls.note.slug,)),
            ('notes:delete', (cls.note.slug,)),
        )

        cls.protected_urls = cls.urls_for_authorized + cls.urls_for_detail_access

    def test_home_available_for_anonymous(self):
        """Главная доступна анониму."""
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_only_pages_available_for_author(self):
        """Автору доступны защищённые страницы."""
        self.client.force_login(self.author)
        for name, args in self.protected_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_only_pages_unavailable_for_other_user(self):
        """Другому пользователю недоступны detail/edit/delete — 404."""
        self.client.force_login(self.other_user)
        for name, args in self.urls_for_detail_access:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_auth_only_pages_redirect_for_anonymous(self):
        """Аноним перенаправляется на логин со всех защищённых страниц."""
        login_url = reverse('users:login')
        for name, args in self.protected_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertTrue(response.url.startswith(login_url))

    def test_public_auth_pages_available(self):
        """Страницы логина, регистрации и выхода доступны всем."""
        for name in ('users:login', 'users:signup', 'users:logout'):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
