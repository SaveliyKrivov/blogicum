from django.shortcuts import get_object_or_404, render
from django.http import Http404
from .models import Post, Category
from django.utils import timezone


def index(request):
    template = 'blog/index.html'
    post_list = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).select_related('category')[:5]
    context = {'post_list': post_list}
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(Category, slug=category_slug)
    if not category.is_published:
        raise Http404()
    post_list = category.posts.filter(
        is_published=True,
        pub_date__lte=timezone.now()
    ).select_related('category')

    context = {'category': category,
               'post_list': post_list}
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'blog/detail.html'
    post = get_object_or_404(
        Post.objects.select_related('category'),
        pk=post_id
    )
    if (not post.is_published
        or not post.category.is_published
            or post.pub_date > timezone.now()):
        raise Http404()
    return render(request, template, {'post': post})
