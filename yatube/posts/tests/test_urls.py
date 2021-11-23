from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Post, Group, Follow

User = get_user_model()


class PostURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Windou')
        self.group = Group.objects.create(slug='Group68')
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_post = self.authorized_client.force_login(self.post.author)

    def test_home_url_guest(self):
        response = self.guest_client.get(reverse(
            'posts:index'))
        self.assertEqual(response.status_code, 200)


    def test_group_auth(self):
        """Сравниваем полученный и ожидаемый."""
        response = requests.get('http://qa-assignment.oblakogroup.ru/board/svetlana_shironina')
        response.status_code == 200)




    def test_home_url_auth(self):
        response = self.authorized_client.get(reverse(
            'posts:index'))
        self.assertEqual(response.status_code, 200)

    def test_group_guest(self):
        response = self.guest_client.get(reverse(
            'posts:group_list', args=[self.group.slug]))
        self.assertEqual(response.status_code, 200)

    def test_group_auth(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list', args=[self.group.slug]))
        self.assertEqual(response.status_code, 200)

    def test_profile_guest(self):
        response = self.guest_client.get(reverse(
            'posts:profile', args=[self.post.author]))
        self.assertEqual(response.status_code, 200)

    def test_profile_auth(self):
        response = self.authorized_client.get(reverse(
            'posts:profile', args=[self.post.author]))
        self.assertEqual(response.status_code, 200)

    def test_post_id_guest(self):
        response = self.guest_client.get(reverse(
            'posts:post_detail', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)

    def test_post_id_auth(self):
        response = self.guest_client.get(reverse(
            'posts:post_detail', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)

    def test_post_id_edit_guest(self):
        response = self.guest_client.get(reverse(
            'posts:post_edit', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)

    def test_post_id_edit_author(self):
        self.authorized_client.get(self.post.author)
        response = self.authorized_client.get(reverse(
            'posts:post_edit', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)

    def test_post_create_guest(self):
        response = self.guest_client.get(reverse(
            'posts:post_create'))
        self.assertRedirects(response, reverse(
            'users:login') + "?next=" + reverse('posts:post_create'))

    def test_post_create_auth(self):
        response = self.authorized_client.get(reverse(
            'posts:post_create'))
        self.assertEqual(response.status_code, 200)

    def test_group_guest(self):
        response = self.guest_client.get(reverse(
            'posts:post_create'))
        self.assertEqual(response.status_code, 302)

    def test_group_auth(self):
        response = self.authorized_client.get(reverse(
            'posts:post_create'))
        self.assertEqual(response.status_code, 200)

    def test_comment_guest(self):
        response = self.guest_client.get(reverse(
            'posts:add_comment', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)

    def test_comment_auth(self):
        response = self.authorized_client.get(reverse(
            'posts:add_comment', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)

    def test_profile_follow_and_unfollow(self):
        author = User.objects.create_user(username='Pushkin')
        response = self.authorized_client.get(reverse(
            'posts:profile_follow', args=[author]))
        self.assertEqual(response.status_code, 302)

    def test_profile_follow_and_unfollow(self):
        author = User.objects.create_user(username='Pushkin')
        Follow.objects.create(user=self.user, author=author)
        response = self.authorized_client.get(reverse(
            'posts:profile_unfollow', args=[author]))
        self.assertEqual(response.status_code, 302)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list',
                                             args=[self.group.slug]),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/post_detail.html': reverse('posts:post_detail',
                                              args=[self.post.id]),
            'posts/profile.html': reverse('posts:profile',
                                          args=[self.user.username]),
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
