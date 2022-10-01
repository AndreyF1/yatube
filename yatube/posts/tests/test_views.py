from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from posts.models import Post, Group, Follow
from posts.utils import POSTS_ON_PAGE

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        test_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='test_gif.gif',
            content=test_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост, больше длинны текста',
            group=cls.group,
            image=uploaded
        )
        cls.group_2 = Group.objects.create(
            title='Пустая группа',
            slug='test_empty',
            description='В этой группе нет постов',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post = PostPagesTests.post
        group = PostPagesTests.group
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': post.author}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': post.pk}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        cache.clear()
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        image_0 = first_object.image
        title = response.context['title']
        self.assertEqual(post_author_0, 'author')
        self.assertEqual(post_text_0, 'Тестовый пост, больше длинны текста')
        self.assertEqual(post_group_0, 'Тестовая группа')
        self.assertEqual(title, 'Последние обновления на сайте')
        self.assertEqual(image_0, PostPagesTests.post.image)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test'}))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        image_0 = first_object.image
        title = response.context['title']
        group = response.context['group']
        self.assertEqual(post_author_0, 'author')
        self.assertEqual(post_text_0, 'Тестовый пост, больше длинны текста')
        self.assertEqual(post_group_0, 'Тестовая группа')
        self.assertEqual(title, f'Записи сообщества {group.slug}')
        self.assertEqual(group.title, 'Тестовая группа')
        self.assertEqual(image_0, PostPagesTests.post.image)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'author'}))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        image_0 = first_object.image
        title = response.context['title']
        author = response.context['author'].username
        self.assertEqual(post_author_0, 'author')
        self.assertEqual(post_text_0, 'Тестовый пост, больше длинны текста')
        self.assertEqual(post_group_0, 'Тестовая группа')
        self.assertEqual(title, f'Записи {post_author_0}')
        self.assertEqual(author, 'author')
        self.assertEqual(image_0, PostPagesTests.post.image)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        post = PostPagesTests.post
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post.pk}))
        object_post = response.context['post'].text
        image = response.context['post'].image
        self.assertEqual(object_post, 'Тестовый пост, больше длинны текста')
        self.assertEqual(image, PostPagesTests.post.image)

    def test_edit_post_show_correct_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        post = PostPagesTests.post
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}))
        form_field = response.context.get('form').fields.get('text')
        self.assertIsInstance(form_field, forms.fields.CharField)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_field = response.context.get('form').fields.get('text')
        self.assertIsInstance(form_field, forms.fields.CharField)

    def test_post_in_right_pages(self):
        """Пост есть на главной странице, в нужной группе и в профайле"""
        post = PostPagesTests.post
        group = PostPagesTests.group
        templates_pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': group.slug}),
            reverse('posts:profile', kwargs={'username': post.author})
        ]
        cache.clear()
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                expected = response.context['page_obj'][0].pk
                self.assertEqual(expected, post.pk)

    def test_post_in_another_group_list(self):
        """Пост не попал в другую группу"""
        post = PostPagesTests.post
        group = PostPagesTests.group_2
        template_page_name = reverse('posts:group_list',
                                     kwargs={'slug': group.slug})
        response = self.authorized_client.get(template_page_name)
        expected = response.context['page_obj']
        self.assertNotIn(post.pk, expected)

    def test_index_cache_check(self):
        """Проверка кэша главной страницы"""
        post_to_delete = Post.objects.create(
            author=self.user,
            text='Кэш пост',
        )
        response = self.authorized_client.get(reverse('posts:index'))
        post_to_delete.delete()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, response_2.content)
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, response_3.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='paginator-terminator')
        cls.group = Group.objects.create(
            title='Paginator group',
            slug='paginator_test',
            description='Тут мы тестируем пагинатор',
        )

        cls.number_of_test_posts: int = POSTS_ON_PAGE + 3
        posts_list = []
        for i in range(cls.number_of_test_posts):
            posts_list.append(Post(
                author=cls.user,
                text=f'Test paginator {i}',
                group=cls.group
            ))
        Post.objects.bulk_create(posts_list)
        cls.post = posts_list[0]

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_right_numbers_of_records(self):
        post = PaginatorViewsTest.post
        group = PaginatorViewsTest.group
        templates_pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': group.slug}),
            reverse('posts:profile', kwargs={'username': post.author})
        ]
        cache.clear()
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 POSTS_ON_PAGE
                                 )

    def test_last_page_contains_right_numbers_of_records(self):
        post = PaginatorViewsTest.post
        group = PaginatorViewsTest.group
        templates_pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': group.slug}),
            reverse('posts:profile', kwargs={'username': post.author})
        ]
        right_number = self.number_of_test_posts - POSTS_ON_PAGE
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']),
                                 right_number
                                 )


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_follower')
        cls.author = User.objects.create_user(username='test_following')
        cls.user_2 = User.objects.create_user(username='test_unfollower')
        cls.post = Post.objects.create(
            author=cls.author,
            text='тестовый пост following'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)

    def test_follow_view(self):
        """Авторизованный пользователь может
        подписываться на других пользователей"""
        follow_count = Follow.objects.filter(user=self.user).count()
        self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.author}
        ))
        self.assertEqual(Follow.objects.filter(user=self.user).count(),
                         follow_count + 1)

    def test_unfollow_view(self):
        """Авторизованный пользователь может
        удалять подписки"""
        unfollow_count = Follow.objects.filter(user=self.user).count()
        self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.author}
        ))
        Follow.objects.filter(user=self.user, author=self.author).delete()
        self.assertEqual(Follow.objects.filter(user=self.user).count(),
                         unfollow_count)

    def test_post_for_followers(self):
        """Пост пользователя появляется в ленте тех, кто на него подписан"""
        self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.author}
        ))
        post = FollowViewsTest.post
        template_page_name = reverse('posts:follow_index')
        response = self.authorized_client.get(template_page_name)
        expected = response.context['page_obj'][0].pk
        self.assertEqual(expected, post.pk)

    def test_post_for_non_followers(self):
        """Пост не появляется в ленте тех, кто не подписан"""
        self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.author}
        ))
        post = FollowViewsTest.post
        template_page_name = reverse('posts:follow_index')
        response = self.authorized_client_2.get(template_page_name)
        expected = response.context['page_obj']
        self.assertNotIn(post.pk, expected)
