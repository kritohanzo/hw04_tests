from datetime import datetime
import shutil
import tempfile
from django.conf import settings

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.views import Group, Post
from django.core.files.uploadedfile import SimpleUploadedFile


User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Dima")
        cls.group = Group.objects.create(
            title="Тестовая группа паджинатора",
            slug="test-group-paginator",
            description="Группа для теста паджинатора",
        )
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

        for i in range(1, 16):
            post = Post.objects.create(
                text="Тестовый пост " + str(i),
                author=cls.user,
                group=cls.group,
            )
            post.pub_date = datetime(2015, 10, i, i, 55, 59, 342380)
            post.save()

        cls.posts = Post.objects.all()

    def test_posts_pages_with_paginators(self):
        """
        Проверяем, соответствует ли ожиданиям
        словарь context cтраниц с паджинатором.
        """
        pages = {
            "posts:index": {},
            "posts:group_list": {"slug": self.group.slug},
            "posts:profile": {"username": self.user.username},
        }
        for page, args in pages.items():
            with self.subTest(page=page):
                response = self.auth_client.get(reverse(page, kwargs=args))
                self.assertEqual(len(response.context["page_obj"]), 10)
                response = self.auth_client.get(
                    reverse(page, kwargs=args) + "?page=2"
                )
                self.assertEqual(len(response.context["page_obj"]), 5)


class TestPostsView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Anton")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-group",
            description="Группа для теста",
        )
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

        cls.post = Post.objects.create(
            text="Тестовый пост 123", author=cls.user, group=cls.group
        )

    def test_posts_views_use_correct_tamplates(self):
        """Проверяем, что все view используют нужный шаблон."""
        tamplates_page_names = {
            "posts/index.html": reverse("posts:index"),
            "posts/group_list.html": reverse(
                "posts:group_list", kwargs={"slug": self.group.slug}
            ),
            "posts/profile.html": reverse(
                "posts:profile", kwargs={"username": self.user.username}
            ),
            "posts/post_detail.html": reverse(
                "posts:post_detail", kwargs={"post_id": self.post.id}
            ),
            "posts/create_post.html": reverse("posts:post_create"),
        }

        for template, reverse_name in tamplates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.auth_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
        response = self.auth_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id})
        )
        template = "posts/create_post.html"
        self.assertTemplateUsed(response, template)

    def test_posts_view_post_detail_context(self):
        """
        Проверяем, соответствует ли ожиданиям
        словарь context страницы /post_detail/.
        """
        response = self.auth_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )
        post_text = response.context["post"].text
        user_posts_count = response.context["posts_count"]
        user_id = response.context["user"]
        self.assertEqual(
            post_text, self.post.text, "В контекст не передаётся текст поста"
        )
        self.assertEqual(
            user_posts_count,
            self.post.author.posts.count(),
            "В контекст не передаётся количество постов автора",
        )
        self.assertEqual(
            user_id,
            self.post.author.id,
            "В контекст не передаётся айди автора",
        )

    def test_posts_view_post_edit_context(self):
        """
        Проверяем, соответствует ли ожиданиям
        словарь context страницы /post_edit/.
        """
        response = self.auth_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id})
        )
        form_object = response.context["form"]
        self.assertIsInstance(
            form_object,
            PostForm,
            "В контекст не передаётся форма редактирования поста",
        )

    def test_posts_view_post_create_context(self):
        """
        Проверяем, соответствует ли ожиданиям
        словарь context страницы /post_create/.
        """
        response = self.auth_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id})
        )
        form_object = response.context["form"]
        self.assertIsInstance(
            form_object,
            PostForm,
            "В контекст не передаётся форма создания поста",
        )

    def test_posts_view_post_create(self):
        """
        Проверяем, что если при создании поста
        указать группу, то этот пост появляется на главной странице сайта,
        на странице выбранной группы, в профайле пользователя."""
        pages = {
            "posts:index": {},
            "posts:group_list": {"slug": self.post.group.slug},
            "posts:profile": {"username": self.post.author},
        }

        for page, args in pages.items():
            with self.subTest(page=page):
                response = self.auth_client.get(reverse(page, kwargs=args))
                self.assertEqual(response.context["post"], self.post)


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestPostsImage(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='Tolya')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа для картинки',
            slug='test-group-image',
            description='Описание тестовой группы'
        )

        cls.small_gif = (            
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост с картинкой',
            group=cls.group,
            author=cls.user,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)




    def test_posts_image_in_context(self):
        '''Проверяем, что при выводе поста с картинкой изображение передаётся в словаре context'''
        response = self.auth_client.get('/')
        self.assertEqual(self.post.image, response.context['page_obj'][self.post.id-1].image, 'Плохо')