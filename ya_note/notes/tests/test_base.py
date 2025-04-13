from django.test import TestCase
from django.contrib.auth import get_user_model
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
            'slug': 'test-slug',
        }

        cls.form_data_updated = {
            'title': 'Новое название',
            'text': 'Обновлённый текст',
            'slug': 'test-slug',
        }
