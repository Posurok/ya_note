from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestPostCreation(TestCase):
    POST_TITLE = 'Заголовок поста'
    POST_TEXT = 'Текст поста'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Барсук владелец')
        cls.reader = User.objects.create(username='Барсук не владелец')
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок',
            text='Текст',
            slug='badger'
        )
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': cls.POST_TITLE,
            'text': cls.POST_TEXT,
            'slug': 'test'
        }

    def setUp(self):
        self.client.force_login(self.author)

    @staticmethod
    def edit_url_for_note(note_slug):
        return reverse('notes:edit', kwargs={'slug': note_slug})

    def test_anonymous_user_cant_create_post_or_edit(self):
        self.client.logout()
        post_data = self.form_data

        response = self.client.post(self.url, data=post_data)
        expected_url = f"{reverse('users:login')}?next=/add/"
        self.assertRedirects(response, expected_url)

        edit_post_url = self.edit_url_for_note(self.note.slug)
        response = self.client.post(edit_post_url, data=post_data)
        expected_url = f"{reverse('users:login')}?next=/edit/{self.note.slug}/"
        self.assertRedirects(response, expected_url)

    def test_non_owner_cant_edit_post(self):
        self.client.logout()
        self.client.force_login(self.reader)
        response = self.client.post(
            self.edit_url_for_note(self.note.slug),
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_slug_transliteration_on_creation(self):
        note = Note.objects.create(
            author=self.author,
            title='Пример Заголовка',
            text='Пример текста'
        )

        expected_slug = 'primer-zagolovka'
        self.assertEqual(note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Проверяем, что автор может редактировать свою заметку."""
        new_title = "Измененный заголовок"
        new_text = "Измененный текст заметки"
        edit_url = self.edit_url_for_note(self.note.slug)
        response = self.client.post(edit_url, {'title': new_title, 'text': new_text})
        self.note.refresh_from_db()

        # Предполагаем, что после успешного редактирования происходит редирект на страницу заметки
        self.assertRedirects(response, reverse('notes:success'))

    def test_author_can_delete_note(self):
        """Проверяем, что автор может удалить свою заметку."""
        delete_url = reverse('notes:delete', kwargs={'slug': self.note.slug})
        response = self.client.post(delete_url)

        # Предполагаем, что после успешного удаления происходит редирект на список заметок
        self.assertRedirects(response, reverse('notes:success'))
        with self.assertRaises(Note.DoesNotExist):
            self.note.refresh_from_db()