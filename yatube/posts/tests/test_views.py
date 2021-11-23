from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from ..models import Post, Group, Follow
from django.core.cache import cache

User = get_user_model()


class PostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user_page')
        cls.group = Group.objects.create(
            title='Заголовок группы',
            slug='test_user_slug',
            description='Тестовое описание',
        )

    def setUp(self):
        self.guest_client = Client()
        self.post = Post.objects.create(
            text='Пост номер 1',
            author=self.user,
            group=self.group)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_did_not_append_other_groups(self):
        """Пост не попадает в чужую группу"""
        new_group = Group.objects.create(
            title='title other group',
            slug='other_group_slug',
            description='Other description')
        response = self.authorized_client.get(reverse('posts:group_list',
                                              kwargs={'slug': new_group.slug}))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_post_did_not_not_append_other_authors(self):
        """Пост не попадает к чужому автору"""
        new_user = User.objects.create_user(username='new_user')
        response = self.authorized_client.get(reverse('posts:profile',
                                              kwargs={'username':
                                                      new_user.username}))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_templates(self):
        templates_page_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list',
                                             args=[self.group.slug]),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/post_detail.html': reverse('posts:post_detail',
                                              args=[self.post.id]),
            'posts/profile.html': reverse('posts:profile',
                                          args=[self.user.username]),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_post_fields(self, post):
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group.id, self.post.group.id)
            self.assertEqual(post.image, self.post.image)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформированы с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.check_post_fields(response.context['page_obj'][0])

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформированы с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        self.check_post_fields(response.context['post'])

    def test_profile_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.context['profile'], self.user)
        self.check_post_fields(response.context['page_obj'][0])

    def test_group_list_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        self.assertEqual(response.context['group'].title, self.group.title)
        self.assertEqual(response.context['group'].slug, self.group.slug)
        self.assertEqual(response.context['group'].description,
                         self.group.description)
        self.check_post_fields(response.context['page_obj'][0])

    def test_post_edit_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=[self.post.id]))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_cache_index(self):
        """Кэш главной страницы работает."""
        response_old = self.authorized_client.get(reverse('posts:index'))
        content_old = response_old.content
        new_post = Post.objects.create(
            author=self.user,
            text='test text',
            group=self.group
        )
        response_new = self.authorized_client.get(reverse('posts:index'))
        content_new = response_new.content
        self.assertEqual(content_old, content_new)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        first_post = response.context['page_obj'][0]
        self.assertEqual(new_post, first_post)

    def test_auth_user_get_follow_author(self):
        """Авторизованный пользователь может подписываться на других
        пользователей.
        """
        Pushkin = User.objects.create_user(username='Pushkin')
        follow_before = Follow.objects.count()
        self.authorized_client.get(
            reverse('posts:profile_follow', args=[Pushkin]))
        response = Follow.objects.filter(
            user=self.user, author=Pushkin).exists()
        self.assertTrue(response)
        self.assertEqual(follow_before + 1, Follow.objects.count())
        latest_follow = Follow.objects.last()
        self.assertEqual(self.user, latest_follow.user)
        self.assertEqual(Pushkin, latest_follow.author)

    def test_auth_user_delete_follow_author(self):
        """Авторизованный пользователь может удалять других пользователей из
        подписок.
        """
        Pushkin = User.objects.create_user(username='Pushkin')
        Follow.objects.create(user=self.user, author=Pushkin)
        follow_before = Follow.objects.count()
        self.authorized_client.get(reverse('posts:profile_unfollow',
                                           args=[Pushkin]))
        response = Follow.objects.filter(user=self.user,
                                         author=Pushkin).exists()
        self.assertFalse(response)
        self.assertEqual(follow_before - 1, Follow.objects.count())

    def test_add_profile_follower(self):
        """Проверка добавления поста у подписчика."""
        Pushkin = User.objects.create_user(username='Pushkin')

        response = self.authorized_client.get(reverse('posts:follow_index'))
        post_count_before = len(response.context['page_obj'])
        Follow.objects.create(user=self.user, author=Pushkin)
        Post.objects.create(
            text='Текст',
            author=Pushkin,
            group=self.group)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']),
                         post_count_before + 1)

    def test_count_follow_other_users(self):
        """Проверка отсутсвия добавленного поста
        у не подписанного пользоваетля.
        """
        Lermontov = User.objects.create_user(username='Lermontov')
        self.authorized_client = Client()
        self.authorized_client.force_login(Lermontov)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        post_count_before = len(response.context['page_obj'])
        self.assertEqual(post_count_before, 0)


class PostPaginatorTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test_user_page')
        self.group = Group.objects.create(
            title='Заголовок группы',
            slug='test_user_slug',
            description='Тестовое описание')
        self.guest_client = Client()

        for post in range(11):
            Post.objects.create(
                author=self.user,
                text='text',
                group=self.group)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator_valid_on_all_templates(self):
        """Пагинатор исправен на всех шаблонах"""
        list_page_one = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.user.username})]

        for page in list_page_one:
            response = self.authorized_client.get(page)
            self.assertEqual(len(response.context['page_obj']), 10)
            response = self.authorized_client.get(page + '?page=2')
            self.assertEqual(len(response.context['page_obj']), 1)
