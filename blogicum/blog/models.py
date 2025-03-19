from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class PublishedModel(models.Model):
    is_published = models.BooleanField(
        verbose_name='Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        verbose_name='Добавлено',
        auto_now_add=True
    )

    class Meta:
        abstract = True


class Category(PublishedModel):
    title = models.CharField(verbose_name='Заголовок', max_length=256)
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        verbose_name='Идентификатор',
        unique=True,
        help_text='Идентификатор страницы для URL; '
                  'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedModel):
    name = models.CharField(verbose_name='Название места', max_length=256)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(PublishedModel):
    title = models.CharField(verbose_name='Заголовок', max_length=256)
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
                  'можно делать отложенные публикации.'
    )
    image = models.ImageField(
        upload_to='posts/',
        null=True,
        blank=True,
        verbose_name='Изображение'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='author',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Местоположение',
        related_name='location',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='category',
    )

    @property
    def comment_count(self):
        return self.post_comment.count()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']

    def __str__(self):
        return self.title


class Comment(PublishedModel):
    text = models.TextField('Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='author_comment'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост',
        related_name='post_comment'
    )
