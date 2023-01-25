from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()
SLICE_OF_THE_FOUND_POST = 15


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название группы")
    slug = models.SlugField(
        unique=True, verbose_name="Ссылка сайта после group/..."
    )
    description = models.TextField(verbose_name="Описание группы")

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name="Текст поста",
        help_text="Текст поста, который увидят пользователи",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата публикации"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
        verbose_name="Группа",
        help_text="Группа, к которой будет относиться запись",
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )  

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:SLICE_OF_THE_FOUND_POST]
