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
