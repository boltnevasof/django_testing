from notes.forms import NoteForm

from .test_base import BaseTestCase


class TestNoteContent(BaseTestCase):

    def test_note_in_list_for_authorized_user(self):
        """Заметка автора отображается в списке и её поля корректны."""
        response = self.authorized_client.get(self.LIST_URL)
        notes = response.context['object_list']

        note = notes.get(pk=self.note.pk)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_other_user_does_not_see_foreign_note(self):
        """Пользователь не видит чужую заметку в списке."""
        response = self.not_author_client.get(self.LIST_URL)
        notes = response.context['object_list']
        self.assertNotIn(self.note, notes)

    def test_author_sees_create_and_edit_form(self):
        """Автор видит формы создания и редактирования заметки."""
        for url in (self.ADD_URL, self.EDIT_URL):
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
