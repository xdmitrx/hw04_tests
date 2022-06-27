from django.db import models
from django.contrib.auth import get_user_model

from . import constants

User = get_user_model()


class Post(models.Model):
    """Создание модели Post."""

    text = models.TextField('Текст поста')
    pub_date = models.DateTimeField('Дата', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts')
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True, null=True,
        verbose_name='Группа')

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        """Строковое представление объекта."""
        return self.text[:constants.SYMBOLS_IN_SELF_TEXT]


class Group(models.Model):
    """Создание модели Group."""

    title = models.CharField('Заголовок', max_length=200,
                             help_text='Заголовок группы.')
    slug = models.SlugField('URL', max_length=200, unique=True,
                            help_text='Уникальный фрагмент адреса.')
    description = models.TextField('Содержание')

    def __str__(self):
        """Возвращает название группы."""
        return self.title
