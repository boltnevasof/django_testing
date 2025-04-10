from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.models import Note

User = get_user_model()


class TestNotesList(TestCase):
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        # Два пользователя: автор и другой
        cls.author = User.objects.create_user(
            username='author',
            password='pass'
        )
        cls.other_user = User.objects.create_user(
            username='other',
            password='pass'
        )

        # Заметки автора
        cls.own_notes = [
            Note.objects.create(
                title=f'Моя заметка {i}',
                text='Текст',
                slug=f'own-{i}',
                author=cls.author
            )
            for i in range(3)
        ]

        # Заметки другого пользователя
        cls.other_notes = [
            Note.objects.create(
                title=f'Чужая заметка {i}',
                text='Текст',
                slug=f'other-{i}',
                author=cls.other_user
            )
            for i in range(2)
        ]

    def test_user_sees_only_own_notes(self):
        """Пользователь видит только свои заметки."""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        notes = response.context['object_list']
        self.assertTrue(all(note.author == self.author for note in notes))
        self.assertEqual(len(notes), len(self.own_notes))

    def test_notes_sorted_old_to_new(self):
        """Заметки отсортированы от старых к новым (по id)."""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        notes = response.context['object_list']
        note_ids = [note.id for note in notes]
        self.assertEqual(note_ids, sorted(note_ids))

    def test_anonymous_cannot_access_list(self):
        """Аноним перенаправляется на логин со страницы списка заметок."""
        response = self.client.get(self.LIST_URL)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)


class TestNoteFormAccess(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст',
            slug='note-slug',
            author=cls.user
        )
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_anonymous_redirected_from_create_form(self):
        """Аноним не может получить доступ к форме создания — редирект."""
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_authorized_user_sees_create_form(self):
        """Авторизованный пользователь видит форму создания."""
        self.client.force_login(self.user)
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form')
        self.assertContains(response, 'name="title"')
        self.assertContains(response, 'name="text"')

    def test_author_sees_edit_form(self):
        """Автор заметки видит форму редактирования."""
        self.client.force_login(self.user)
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form')
        self.assertContains(response, 'name="title"')
        self.assertContains(response, 'name="text"')
