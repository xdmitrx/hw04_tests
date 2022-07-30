from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group
from ..forms import PostForm


User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.post = Post.objects.create(
            author=cls.user,
            text='test post',
        )
        cls.form = PostForm()
        cls.group_1 = Group.objects.create(
            title='test title 1',
            slug='23',
            description='test description 1',
        )
        cls.group_2 = Group.objects.create(
            title='test title 2',
            slug='25',
            description='Теst description 2',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authorized_client_post_create(self):
        """Публикация поста авторизованным пользователем."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'test post',
            'group': self.group_1.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        last_post = Post.objects.first()
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': f'{self.user.username}'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        last_post_data = ((last_post.text, form_data.get('text')),
                          (last_post.group.title, self.group_1.title),
                          (last_post.author, self.user))
        for value, expected in last_post_data:
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_authorized_client_post_edit(self):
        """Изменение поста авторизованным пользователем."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'test post edit post',
            'group': self.group_2.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True
        )
        last_edit_post = Post.objects.get(id=self.post.id)
        self.assertRedirects(response, reverse(
            'posts:post_edit',
            kwargs={'post_id': f'{self.post.id}'}))
        self.assertEqual(Post.objects.count(), posts_count)
        last_edit_post_data = ((last_edit_post.text, form_data.get('text')),
                               (last_edit_post.group.title,
                                self.group_2.title),
                               (last_edit_post.author, self.user))
        for value, expected in last_edit_post_data:
            with self.subTest(value=value):
                self.assertEqual(value, expected)
