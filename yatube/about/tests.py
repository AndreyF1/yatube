from http.client import responses

from django.contrib.auth import get_user_model
from django.test import TestCase, Client


User = get_user_model()


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_404(self):
        """Несуществующая страница."""
        url = '/unexisting_page/'
        response = self.guest_client.get(url)
        self.assertEqual(responses[response.status_code], 'Not Found')

    def test_urls(self):
        """проверка доступности страниц приложения About"""
        urls = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for url, expected_template in urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                enam_http = responses[response.status_code]
                self.assertTemplateUsed(response, expected_template)
                self.assertEqual(enam_http, 'OK')
