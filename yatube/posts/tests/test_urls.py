from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post


User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.user2 = User.objects.create_user(username='test_author')
        cls.group = Group.objects.create(
            title='test title',
            slug='1',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.user2,
            text='test post',
        )

    def setUp(self):
        self.guest = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(TaskURLTests.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(TaskURLTests.user2)

    def test_urls_uses_correct_template(self):
        """Проверит, что страницы используют правильные шаблоны."""
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

    def test_index_page_not_login_user(self):
        """Главная страница доступна гостю."""
        index_page = '/'
        response = self.guest.get(index_page)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_page_not_login_user(self):
        """Просмотр групп доступен гостю."""
        group_page = f'/group/{TaskURLTests.group.slug}/'
        response = self.guest.get(group_page, args=[self.group.slug])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_page_not_login_user(self):
        """Просмотр чужого профиля доступен гостю."""
        profile_page = f'/profile/{TaskURLTests.user.username}/'
        response = self.guest.get(profile_page, args=[self.user.username])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_page_not_login_user(self):
        """Просмотр чужого поста доступен гостю."""
        post_page = f'/posts/{TaskURLTests.post.id}/'
        response = self.guest.get(post_page)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_authorized_client(self):
        """Создавать пост может только авторизованный пользователь."""
        create_post_page = '/create/'
        response = self.authorized_client.get(create_post_page)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_authorized_client(self):
        """Редактирование поста автором."""
        edit_post_page = f'/posts/{TaskURLTests.post.id}/edit/'
        response = self.authorized_client2.get(edit_post_page)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_non_exist_page(self):
        """Тест на ошибку 404"""
        unexisting_page = '/unexisting_page/'
        response = self.authorized_client.get(unexisting_page)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
