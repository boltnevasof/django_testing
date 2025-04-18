from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

# Константы
SLUG = 'test-slug'

HOME_URL = reverse('notes:home')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
DETAIL_URL = reverse('notes:detail', args=[SLUG])
EDIT_URL = reverse('notes:edit', args=[SLUG])
DELETE_URL = reverse('notes:delete', args=[SLUG])

LOGIN_LIST_REDIRECT = f'{LOGIN_URL}?next={LIST_URL}'
LOGIN_SUCCESS_REDIRECT = f'{LOGIN_URL}?next={SUCCESS_URL}'
LOGIN_ADD_REDIRECT = f'{LOGIN_URL}?next={ADD_URL}'
LOGIN_DETAIL_REDIRECT = f'{LOGIN_URL}?next={DETAIL_URL}'
LOGIN_EDIT_REDIRECT = f'{LOGIN_URL}?next={EDIT_URL}'
LOGIN_DELETE_REDIRECT = f'{LOGIN_URL}?next={DELETE_URL}'

User = get_user_model()


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author', password='pass'
        )
        cls.not_author = User.objects.create_user(
            username='not_author', password='pass'
        )

        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст',
            author=cls.author,
            slug=SLUG,
        )

        cls.authorized_client = cls.client_class()
        cls.authorized_client.force_login(cls.author)

        cls.not_author_client = cls.client_class()
        cls.not_author_client.force_login(cls.not_author)

        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст заметки',
            'slug': 'another-slug',
        }
