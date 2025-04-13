from http import HTTPStatus
from .test_base import BaseTestCase
from .test_urls import list_url, add_url, edit_url, login_url


class TestNoteContent(BaseTestCase):

    def test_user_sees_only_own_notes(self):
        """Пользователь видит только свои заметки."""
        self.authorized_client.force_login(self.author)
        response = self.authorized_client.get(list_url())
        notes = response.context['page_obj']
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0], self.note)

    def test_notes_sorted_old_to_new(self):
        """Заметки отсортированы от старых к новым по id."""
        response = self.authorized_client.get(list_url())
        notes = response.context['object_list']
        note_ids = [note.id for note in notes]
        self.assertEqual(note_ids, sorted(note_ids))

    def test_anonymous_cannot_access_list(self):
        """Аноним перенаправляется на логин со страницы списка заметок."""
        response = self.client.get(list_url())
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(response.url.startswith(f'{login_url()}?next='))

    def test_author_sees_create_and_edit_form(self):
        """Автор видит формы создания и редактирования заметки."""
        for url in (add_url(), edit_url()):
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertIn('form', response.context)
                form = response.context['form']
                self.assertIn('title', form.fields)
                self.assertIn('text', form.fields)
