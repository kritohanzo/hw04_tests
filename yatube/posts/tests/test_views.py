from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.views import Group, Post


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
        [POSTS VIEWS] Проверяем, соответствует ли ожиданиям
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
        """[POSTS VIEWS] Проверяем, что все view используют нужный шаблон."""
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
        [POSTS VIEWS] Проверяем, соответствует ли ожиданиям
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
        [POSTS VIEWS] Проверяем, соответствует ли ожиданиям
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
        [POSTS VIEWS] Проверяем, соответствует ли ожиданиям
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
        """[POSTS VIEWS] Проверяем, что если при создании поста
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
