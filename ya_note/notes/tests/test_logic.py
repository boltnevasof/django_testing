from http import HTTPStatus

from pytils.translit import slugify

from notes.models import Note
from .test_base import BaseTestCase


class TestNoteLogic(BaseTestCase):
    def test_authorized_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        notes_before = set(Note.objects.values_list('pk', flat=True))
        response = self.authorized_client.post(
            self.ADD_URL, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        notes_after = Note.objects.exclude(pk__in=notes_before)
        self.assertEqual(notes_after.count(), 1)

        note = notes_after.first()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_before = set(Note.objects.values_list('pk', flat=True))
        response = self.client.post(self.ADD_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        notes_after = set(Note.objects.values_list('pk', flat=True))
        self.assertEqual(notes_before, notes_after)

    def test_slug_is_generated_if_empty(self):
        """Slug создаётся автоматически при отсутствии."""
        self.form_data.pop('slug')
        notes_before = set(Note.objects.values_list('pk', flat=True))

        response = self.authorized_client.post(
            self.ADD_URL, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        notes_after = Note.objects.exclude(pk__in=notes_before)
        self.assertEqual(notes_after.count(), 1)

        note = notes_after.first()
        expected_slug = slugify(self.form_data['title'])

        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, expected_slug)
        self.assertEqual(note.author, self.author)

    def test_slug_must_be_unique(self):
        """Два одинаковых slug запрещены."""
        self.form_data['slug'] = self.note.slug
        notes_before = set(Note.objects.all())
        response = self.authorized_client.post(
            self.ADD_URL, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFormError(
            response, 'form', 'slug',
            f'{self.note.slug} - такой slug уже существует, '
            'придумайте уникальное значение!'
        )
        notes_after = set(Note.objects.all())
        self.assertSetEqual(notes_after, notes_before)

    def test_author_can_edit_note(self):
        """Автор может редактировать заметку."""
        response = self.authorized_client.post(
            self.EDIT_URL, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.note.author)

    def test_not_author_cannot_edit_note(self):
        """Неавтор не может редактировать чужую заметку."""
        response = self.not_author_client.post(
            self.EDIT_URL, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        notes_count_before = Note.objects.count()
        response = self.authorized_client.post(self.DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), notes_count_before - 1)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_not_author_cannot_delete_note(self):
        """Неавтор не может удалить чужую заметку."""
        note_before = Note.objects.get(pk=self.note.pk)

        response = self.not_author_client.post(self.DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())

        note_after = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note_after.title, note_before.title)
        self.assertEqual(note_after.text, note_before.text)
        self.assertEqual(note_after.slug, note_before.slug)
        self.assertEqual(note_after.author, note_before.author)
