from http.client import responses

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_2 = User.objects.create_user(username='signed_in')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост, больше длинны текста',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.signed_in_client = Client()
        self.signed_in_client.force_login(self.user_2)

    def test_404(self):
        """Несуществующая страница."""
        url = '/unexisting_page/'
        response = self.guest_client.get(url)
        self.assertEqual(responses[response.status_code], 'Not Found')

    def test_urls_guest(self):
        """Доступные страницы для гостя"""
        post = PostURLTests.post
        urls = {
            '/': 'posts/index.html',
            '/group/test/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            f'/posts/{post.pk}/': 'posts/post_detail.html',
        }
        cache.clear()
        for url, expected_template in urls.items():
            with self.subTest(url=url):
                response_guest = self.guest_client.get(url)
                enam_http = responses[response_guest.status_code]
                self.assertTemplateUsed(response_guest, expected_template)
                self.assertEqual(enam_http, 'OK')
        response_auth = self.guest_client.get('/create/')
        enam_http = responses[response_auth.status_code]
        self.assertEqual(enam_http, 'Found')

    def test_urls_auth(self):
        """Доступные страницы для автора"""
        post = PostURLTests.post
        urls = {
            '/': 'posts/index.html',
            '/group/test/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            f'/posts/{post.pk}/': 'posts/post_detail.html',
            f'/posts/{post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for url, expected_template in urls.items():
            with self.subTest(url=url):
                response_auth = self.authorized_client.get(url)
                enam_http = responses[response_auth.status_code]
                self.assertTemplateUsed(response_auth, expected_template)
                self.assertEqual(enam_http, 'OK')

    def test_urls_signed_in(self):
        """Доступные страницы для авторизованного пользователя (не автора)"""
        post = PostURLTests.post
        urls = {
            '/': 'posts/index.html',
            '/group/test/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            f'/posts/{post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
        }
        cache.clear()
        for url, expected_template in urls.items():
            with self.subTest(url=url):
                response_auth = self.signed_in_client.get(url)
                enam_http = responses[response_auth.status_code]
                self.assertTemplateUsed(response_auth, expected_template)
                self.assertEqual(enam_http, 'OK')
        response_auth = self.signed_in_client.get(f'/posts/{post.pk}/edit/')
        enam_http = responses[response_auth.status_code]
        self.assertEqual(enam_http, 'Found')
