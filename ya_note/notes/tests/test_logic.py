from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.create_url = reverse('notes:add')
        cls.form_data = {
            'title': 'Заголовок',
            'text': cls.NOTE_TEXT,
            'slug': 'test-slug'
        }

    def test_authorized_user_can_create_note(self):
        # Авторизованный пользователь может создать заметку
        response = self.auth_client.post(self.create_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Note.objects.filter(slug='test-slug').exists())

    def test_anonymous_user_cannot_create_note(self):
        # Анонимный пользователь не может создать заметку
        self.client.post(self.create_url, data=self.form_data)
        self.assertFalse(Note.objects.filter(slug='test-slug').exists())

    def test_slug_is_generated_if_empty(self):
        title = 'Заметка без слага'
        data = {'title': title, 'text': 'Текст без слага'}
        self.auth_client.post(self.create_url, data=data)

        expected_slug = slugify(title)
        self.assertTrue(Note.objects.filter(slug=expected_slug).exists())

    def test_slug_must_be_unique(self):
        # Два одинаковых slug запрещены
        Note.objects.create(
            title='Старая заметка',
            text='Первоначальный текст заметки',
            slug='same-slug',
            author=self.user
        )
        data = {
            'title': 'Новая заметка',
            'text': 'Попытка дублирования',
            'slug': 'same-slug'
        }
        response = self.auth_client.post(self.create_url, data=data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFormError(
            response,
            'form',
            'slug',
            'same-slug - такой slug уже существует,'
            'придумайте уникальное значение!'
        )


class TestNoteEditDelete(TestCase):
    INITIAL_TEXT = 'Начальный текст'
    UPDATED_TEXT = 'Обновлённый текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Автор')
        cls.other = User.objects.create_user(username='Чужой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.other_client = Client()
        cls.other_client.force_login(cls.other)

        cls.note = Note.objects.create(
            title='Заметка',
            text=cls.INITIAL_TEXT,
            slug='note-slug',
            author=cls.author
        )

        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.note.title,
            'text': cls.UPDATED_TEXT,
            'slug': cls.note.slug
        }

    def test_author_can_edit_note(self):
        # Автор может редактировать заметку
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.UPDATED_TEXT)

    def test_other_user_cannot_edit_note(self):
        # Другой пользователь не может редактировать чужую заметку
        response = self.other_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.INITIAL_TEXT)

    def test_author_can_delete_note(self):
        # Автор может удалить заметку
        response = self.author_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_other_user_cannot_delete_note(self):
        # Другой пользователь не может удалить чужую заметку
        response = self.other_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())