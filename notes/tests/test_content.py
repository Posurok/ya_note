from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()

class NoteContentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='user1')
        cls.user2 = User.objects.create_user(username='user2')
        cls.note1 = Note.objects.create(
            author=cls.user1,
            title='User 1 Note',
            text='Text', slug='user-1-note'
        )
        cls.note2 = Note.objects.create(
            author=cls.user2,
            title='User 2 Note',
            text='Text',
            slug='user-2-note'
        )

    def test_note_list_context(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse('notes:list'))
        self.assertIn('object_list', response.context)
        self.assertTrue(self.note1 in response.context['object_list'])
        self.assertFalse(self.note2 in response.context['object_list'])

    def test_add_note_page_context(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse('notes:add'))
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_note_page_context(self):
        self.client.force_login(self.user1)
        response = self.client.get(
            reverse('notes:edit', kwargs={'slug': self.note1.slug})
        )
        self.assertIsInstance(response.context['form'], NoteForm)
        self.assertEqual(response.context['form'].instance, self.note1)
