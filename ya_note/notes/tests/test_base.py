from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author', password='pass'
        )
        cls.other_user = User.objects.create_user(
            username='other', password='pass'
        )
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст',
            author=cls.author,
            slug='test-slug',
        )
        cls.authorized_client = cls.client_class()
        cls.authorized_client.force_login(cls.author)
        cls.other_client = cls.client_class()
        cls.other_client.force_login(cls.other_user)

        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст заметки',
            'slug': 'another-slug',
        }
        cls.HOME_URL = reverse('notes:home')
        cls.LOGIN_URL = reverse('users:login')
        cls.LOGOUT_URL = reverse('users:logout')
        cls.SIGNUP_URL = reverse('users:signup')
        cls.LIST_URL = reverse('notes:list')
        cls.ADD_URL = reverse('notes:add')
        cls.SUCCESS_URL = reverse('notes:success')

        cls.DETAIL_URL = reverse('notes:detail', args=[cls.note.slug])
        cls.EDIT_URL = reverse('notes:edit', args=[cls.note.slug])
        cls.DELETE_URL = reverse('notes:delete', args=[cls.note.slug])

        cls.LOGIN_REDIRECTS = [
            (cls.LIST_URL, f'{cls.LOGIN_URL}?next={cls.LIST_URL}'),
            (cls.SUCCESS_URL, f'{cls.LOGIN_URL}?next={cls.SUCCESS_URL}'),
            (cls.ADD_URL, f'{cls.LOGIN_URL}?next={cls.ADD_URL}'),
            (cls.DETAIL_URL, f'{cls.LOGIN_URL}?next={cls.DETAIL_URL}'),
            (cls.EDIT_URL, f'{cls.LOGIN_URL}?next={cls.EDIT_URL}'),
            (cls.DELETE_URL, f'{cls.LOGIN_URL}?next={cls.DELETE_URL}'),
        ]
