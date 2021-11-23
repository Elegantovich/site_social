from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Time(models.Model):

    created = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        abstract = True


class Group(models.Model):
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    title = models.CharField(max_length=200, default="default title")

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(help_text='Текст нового поста',
                            verbose_name='Текст поста')
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts")
    group = models.ForeignKey(
        Group,
        help_text='Группа, к которой будет относиться пост',
        verbose_name='Группа',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="posts")
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True)

    class Meta():
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:15]


class Comment(Time):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             verbose_name="Пост",
                             related_name="comments")
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name="Автор",
                               related_name="comments")
    text = models.TextField(verbose_name="Текст комментария",
                            help_text="Текст нового комментария")

    class Meta():
        ordering = ["-created"]

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.SET_NULL,
                             null=True,
                             verbose_name='Подсписчик',
                             related_name='follower')
    author = models.ForeignKey(User,
                               on_delete=models.SET_NULL,
                               null=True,
                               verbose_name='Автор',
                               related_name='following')
