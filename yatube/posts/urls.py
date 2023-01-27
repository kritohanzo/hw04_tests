from django.urls import path

from . import views
from posts.views import PostCreateView, CommentCreateView

app_name = "posts"

urlpatterns = [
    path("", views.index, name="index"),
    path("group/<slug:slug>/", views.group_posts, name="group_list"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path("create/", PostCreateView.as_view(), name="post_create"),
    path("posts/<int:post_id>/edit/", views.post_edit, name="post_edit"),
    path("posts/<int:post_id>/comment/", CommentCreateView.as_view(), name='add_comment')
]
