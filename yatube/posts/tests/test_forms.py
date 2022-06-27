from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post
from ..forms import PostForm


User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTest.user)

    def test_post_create(self):
        """Валидная форма создает запись Post."""
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': f'{PostFormTest.user.username}'}))
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
            ).exists()
        )

    def test_post_edit(self):
        """Валидная форма изменяет запись Post."""
        form_data = {
            'text': 'Текстовый отредактированный пост',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{PostFormTest.post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_edit',
            kwargs={'post_id': f'{PostFormTest.post.id}'}))
        self.assertTrue(
            Post.objects.filter(
                text='Текстовый отредактированный пост',
            ).exists()
        )
