from http import HTTPStatus

from pytils.translit import slugify

from notes.models import Note

from .test_base import BaseTestCase
from .test_urls import ADD_URL, EDIT_URL, DELETE_URL


class TestNoteLogic(BaseTestCase):

    def test_authorized_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        unique_slug = 'unique-slug'
        self.form_data['slug'] = unique_slug

        response = self.authorized_client.post(ADD_URL, data=self.form_data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Note.objects.filter(slug=unique_slug).exists())

        note = Note.objects.get(slug=unique_slug)
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_before = Note.objects.count()
        response = self.client.post(ADD_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), notes_before)

    def test_slug_is_generated_if_empty(self):
        """Slug создаётся автоматически при отсутствии."""
        self.form_data.pop('slug')
        self.form_data['title'] = 'Заметка без слага'
        self.form_data['text'] = 'Текст'

        self.authorized_client.post(ADD_URL, data=self.form_data)

        expected_slug = slugify(self.form_data['title'])
        self.assertTrue(Note.objects.filter(slug=expected_slug).exists())

        note = Note.objects.get(slug=expected_slug)
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.author)

    def test_slug_must_be_unique(self):
        """Два одинаковых slug запрещены."""
        self.form_data['slug'] = self.note.slug  # совпадает с уже существующей

        notes_before = list(Note.objects.all())
        response = self.authorized_client.post(ADD_URL, data=self.form_data)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFormError(
            response, 'form', 'slug',
            f'{self.note.slug} - такой slug уже существует, '
            'придумайте уникальное значение!'
        )
        notes_after = list(Note.objects.all())
        self.assertListEqual(notes_after, notes_before)

    def test_author_can_edit_note(self):
        """Автор может редактировать заметку."""
        original_author = self.note.author

        response = self.authorized_client.post(
            EDIT_URL, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])

        self.assertEqual(note.author, original_author)

    def test_other_user_cannot_edit_note(self):
        """Другой пользователь не может редактировать чужую заметку."""
        original_note = Note.objects.get(pk=self.note.pk)

        response = self.other_client.post(
            EDIT_URL, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, original_note.title)
        self.assertEqual(note.text, original_note.text)
        self.assertEqual(note.slug, original_note.slug)
        self.assertEqual(note.author, original_note.author)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        notes_before = set(Note.objects.values_list('pk', flat=True))

        response = self.authorized_client.post(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        notes_after = set(Note.objects.values_list('pk', flat=True))
        self.assertEqual(notes_after, notes_before - {self.note.pk})

    def test_other_user_cannot_delete_note(self):
        """Другой пользователь не может удалить чужую заметку."""
        original_note = Note.objects.get(pk=self.note.pk)
        notes_before = list(Note.objects.all())

        response = self.other_client.post(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        notes_after = list(Note.objects.all())
        self.assertEqual(notes_after, notes_before)

        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, original_note.title)
        self.assertEqual(note.text, original_note.text)
        self.assertEqual(note.slug, original_note.slug)
        self.assertEqual(note.author, original_note.author)
