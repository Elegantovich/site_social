from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelPostTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='auth')
        self.post = Post.objects.create(author=self.user,
                                        text='Тест поста более 15 символов')

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(self.post.text[:15], str(self.post))


class PostModelGroupTest(TestCase):
    def setUp(self):
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание')

    def test_models_have_correct_object_names(self):
        self.assertEqual(self.group.title, str(self.group))
