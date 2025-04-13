from http import HTTPStatus

from pytils.translit import slugify
from notes.models import Note

from .test_base import BaseTestCase
from .test_urls import add_url, edit_url, delete_url
from notes.tests.test_urls import CREATE_URL


class TestNoteLogic(BaseTestCase):

    def test_authorized_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        self.form_data['slug'] = 'unique-slug'
        response = self.authorized_client.post(add_url(), data=self.form_data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 2)
        note = Note.objects.latest('id')
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        self.client.post(CREATE_URL, data=self.form_data)
        self.assertFalse(
            Note.objects.filter(title=self.form_data['title']).exists()
        )

    def test_slug_is_generated_if_empty(self):
        """Slug создаётся автоматически при отсутствии."""
        data = {
            'title': 'Заметка без слага',
            'text': 'Текст',
        }
        self.authorized_client.post(add_url(), data=data)
        self.assertEqual(Note.objects.count(), 2)
        note = Note.objects.exclude(pk=self.note.pk).get()
        self.assertEqual(note.slug, slugify(data['title']))
        self.assertEqual(note.title, data['title'])
        self.assertEqual(note.text, data['text'])
        self.assertEqual(note.author, self.author)

    def test_slug_must_be_unique(self):
        """Два одинаковых slug запрещены."""
        Note.objects.create(
            title='Старая заметка',
            text='Текст',
            slug='same-slug',
            author=self.author
        )
        data = {
            'title': 'Новая заметка',
            'text': 'Другой текст',
            'slug': 'same-slug'
        }
        response = self.authorized_client.post(add_url(), data=data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFormError(
            response, 'form', 'slug',
            'same-slug - такой slug уже существует, '
            'придумайте уникальное значение!'
        )
        self.assertEqual(Note.objects.count(), 2)

    def test_author_can_edit_note(self):
        """Автор может редактировать заметку."""
        response = self.authorized_client.post(
            edit_url(), data=self.form_data_updated
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, self.form_data_updated['title'])
        self.assertEqual(note.text, self.form_data_updated['text'])
        self.assertEqual(note.slug, self.form_data_updated['slug'])
        self.assertEqual(note.author, self.author)

    def test_other_user_cannot_edit_note(self):
        """Другой пользователь не может редактировать чужую заметку."""
        response = self.other_client.post(
            edit_url(), data=self.form_data_updated
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.author)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        response = self.authorized_client.post(delete_url())
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cannot_delete_note(self):
        """Другой пользователь не может удалить чужую заметку."""
        response = self.other_client.post(delete_url())
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.author)
