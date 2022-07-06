from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..import constants

from ..models import Group, Post

User = get_user_model()


class PostsViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_username')
        cls.group = Group.objects.create(
            title='test title',
            slug='1',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test post',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewTests.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        reverse_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{PostsViewTests.post.id}'}):
            'posts/create_post.html',
            reverse('posts:profile',
                    kwargs={'username': f'{PostsViewTests.user.username}'}):
            'posts/profile.html',
            reverse('posts:group_list',
                    kwargs={'slug': f'{PostsViewTests.group.slug}'}):
            'posts/group_list.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{PostsViewTests.post.id}'}):
            'posts/post_detail.html',
        }
        for reverse_name, template in reverse_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class PostsPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_username')
        cls.group = Group.objects.create(
            title='test title',
            slug='1',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test post',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsPagesTest.user)

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_obj = response.context['page_obj'][0]
        self.assertEqual(first_obj.text, 'test post')
        self.assertEqual(first_obj.author.username, 'test_username')
        self.assertEqual(first_obj.group.title, 'test title')

    def test_task_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': f'{PostsPagesTest.group.slug}'}
        ))
        first_obj = response.context['page_obj'][0]
        self.assertEqual(first_obj.text, 'test post')
        self.assertEqual(first_obj.author.username, 'test_username')
        self.assertEqual(first_obj.group.title, 'test title')
        self.assertEqual(response.context['group'].title, 'test title')

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': f'{PostsPagesTest.user.username}'}
        ))
        first_obj = response.context['page_obj'][0]
        self.assertEqual(first_obj.text, 'test post')
        self.assertEqual(first_obj.author.username, 'test_username')
        self.assertEqual(first_obj.group.title, 'test title')
        self.assertEqual(response.context['author'].username,
                         'test_username')

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': f'{PostsPagesTest.post.id}'}
        ))
        obj = response.context['post']
        self.assertEqual(obj.text, 'test post')
        self.assertEqual(obj.author.username, 'test_username')
        self.assertEqual(obj.group.title, 'test title')

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': f'{PostsPagesTest.post.id}'}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_username')
        cls.posts = [Post.objects.create(
            author=cls.user,
            text='test post'
        ) for i in range(constants.POSTS_PER_PAGE
                         + constants.POSTS_PER_SECOND_PAGE)
        ]

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)

    def test_first_page_contains_ten_records(self):
        """Проверит количество постов на первой странице."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']),
                            (constants.POSTS_PER_PAGE)
                         )

    def test_second_page_contains_three_records(self):
        """Проверит количество постов на второй странице."""
        response = self.authorized_client.get(reverse(
            'posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']),
                            (constants.POSTS_PER_SECOND_PAGE)
                         )
