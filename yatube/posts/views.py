from django.shortcuts import render, get_object_or_404
from .models import Post, Group, User, Follow
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from django.shortcuts import redirect
from .utils import get_pages
from django.views.decorators.cache import cache_page


@cache_page(20)
def index(request):
    post_list = Post.objects.all()
    template = 'posts/index.html'
    page_obj = get_pages(post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group)
    page_obj = get_pages(post_list, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author)
    title = f'Записи {username}'
    page_obj = get_pages(post_list, request)
    following = (request.user.is_authenticated
                 and Follow.objects.filter(user=request.user,
                                           author=author).exists())
    context = {
        'author': author,
        'title': title,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'form': form,
        'post': post,
        'comments': comments,
        'post_id': post_id,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    is_edit = False
    form = PostForm(request.POST or None,
                    files=request.FILES or None
                    )
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', username=request.user)
    template_name = 'posts/create_post.html'
    return render(request, template_name, {'form': form, 'is_edit': is_edit})


@login_required
def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(Post, id=post_id)
    if request.user.id != post.author.id:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        post.save()
        return redirect('posts:post_detail', post_id=post_id)
    template_name = 'posts/create_post.html'
    return render(request, template_name,
                  {'form': form, 'is_edit': is_edit, 'post': post}
                  )


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user
    )
    title = 'Мои подписки'
    page_obj = get_pages(posts, request)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    if request.user != get_object_or_404(User, username=username):
        Follow.objects.get_or_create(
            user=request.user,
            author=User.objects.get(username=username)
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    if Follow.objects.filter(
            user=request.user, author__username=username).exists():
        Follow.objects.filter(
            user=request.user, author__username=username
        ).delete()
    return redirect('posts:profile', username=username)
