from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post


User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.user2 = User.objects.create_user(username='test_user2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='1',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(TaskURLTests.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(TaskURLTests.user2)

    def test_urls_uses_correct_template(self):
        '''Проверит, что страницы используют правильные шаблоны.'''
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{TaskURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{TaskURLTests.user.username}/': 'posts/profile.html',
            f'/posts/{TaskURLTests.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{TaskURLTests.post.id}/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_non_exist_page(self):
        """Тест на ошибку 404"""
        unexisting_page = '/unexisting_page/'
        response = self.authorized_client.get(unexisting_page)
        self.assertEqual(response.status_code, 404)
