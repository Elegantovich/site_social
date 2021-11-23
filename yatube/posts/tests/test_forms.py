import shutil
import tempfile
from ..models import Post, Group, Comment
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(slug='test_slug',
                                         description='test description',
                                         title='Test TITLE')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post моделе."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {'text': 'NEW текст',
                     'group': self.group.id,
                     'image': uploaded}
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': self.user.username}))
        latest_post = Post.objects.last()
        self.assertEqual(self.group, latest_post.group)
        self.assertEqual(self.user, latest_post.author)
        self.assertEqual(form_data['text'], latest_post.text)
        self.assertTrue(
            latest_post.image.name.endswith(form_data['image'].name))

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post моделе."""
        new_post = Post.objects.create(text='Тестовый текст2',
                                            author=self.user,
                                            group=self.group)
        form_data = {'text': 'edit текст',
                     'group': self.group.id}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': new_post.id}),
            data=form_data,
            follow=True)
        post_new = Post.objects.get(id=new_post.id)
        self.assertEqual(post_new.text, form_data['text'])
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': new_post.id}))

    def test_comment_post(self):
        """Валидная форма создает запись в Comment моделе"""
        new_post = Post.objects.create(text='Тестовый текст2',
                                            author=self.user,
                                            group=self.group)
        comment_before = Comment.objects.count()
        form_data = {'text': 'test_comments'}
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': new_post.id}),
            data=form_data,
            follow=True)
        latest_comment = Comment.objects.last()
        self.assertEqual(self.user, latest_comment.author)
        self.assertEqual(form_data['text'], latest_comment.text)
        self.assertEqual(new_post, latest_comment.post)
        self.assertEqual(comment_before + 1, Comment.objects.count())
