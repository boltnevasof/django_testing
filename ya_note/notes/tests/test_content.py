from notes.forms import NoteForm

from .test_base import BaseTestCase
from .test_urls import LIST_URL, ADD_URL, EDIT_URL


class TestNoteContent(BaseTestCase):

    def test_note_in_list_for_authorized_user(self):
        """Заметка автора отображается в списке и её поля корректны."""
        response = self.authorized_client.get(LIST_URL)
        notes = response.context['page_obj']
        self.assertIn(self.note, notes)
        note = notes[0]
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_other_user_does_not_see_foreign_note(self):
        """Пользователь не видит чужую заметку в списке."""
        response = self.other_client.get(LIST_URL)
        notes = response.context['page_obj']
        self.assertNotIn(self.note, notes)

    def test_author_sees_create_and_edit_form(self):
        """Автор видит формы создания и редактирования заметки."""
        for url in (ADD_URL, EDIT_URL):
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertIsInstance(response.context['form'], NoteForm)
