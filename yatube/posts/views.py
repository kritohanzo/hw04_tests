from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


POSTS_PER_PAGE = 10


def paginator(request, queryset, number_page):
    paginator = Paginator(queryset, number_page)
    page_number = request.GET.get("page")
    page_object = paginator.get_page(page_number)
    return page_object


def index(request):
    posts = Post.objects.all()
    page_obj = paginator(request, posts, POSTS_PER_PAGE)
    template = "posts/index.html"
    context = {"page_obj": page_obj}
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginator(request, posts, POSTS_PER_PAGE)
    template = "posts/group_list.html"
    context = {"group": group, "page_obj": page_obj}
    return render(request, template, context)


def profile(request, username):
    author = User.objects.get(username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    template = "posts/profile.html"
    context = {"page_obj": page_obj, "username": author}
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    posts_count = author.posts.count()
    template = "posts/post_detail.html"
    context = {
        "post": post,
        "posts_count": posts_count,
        "user": request.user.id,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("posts:profile", username=post.author.username)
        template = "posts/create_post.html"
        context = {"form": form}
        return render(request, template, context)
    form = PostForm()
    template = "posts/create_post.html"
    context = {"form": form}
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author_id != request.user.id:
        return redirect("posts:post_detail", post_id=post.pk)
    if request.method == "POST":
        form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect("posts:post_detail", post_id=post.pk)
        template = "posts/create_post.html"
        context = {"form": form}
        return render(request, template, context)
    form = PostForm(instance=post)
    template = "posts/create_post.html"
    context = {"form": form, "is_edit": 1, "post": post}
    return render(request, template, context)
