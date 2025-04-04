from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse, reverse_lazy
from django.http import Http404
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm
from django.utils import timezone
from django.views.generic import CreateView, ListView
from django.views.generic import UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User


class IndexListView(ListView):
    model = Post
    queryset = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).select_related('category')
    ordering = '-pub_date'
    paginate_by = 10
    template_name = 'blog/index.html'


class ProfileDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        username = self.kwargs.get('username')
        return get_object_or_404(User, username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_owner = self.object
        posts = Post.objects.filter(author=page_owner).order_by('-pub_date')

        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page', 1)
        context['page_obj'] = paginator.get_page(page_number)
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ['username', 'first_name', 'last_name', 'email']

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', 
                       kwargs={'username': self.request.user.username})


class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = 10
    ordering = '-pub_date'

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        self.category = get_object_or_404(Category, slug=category_slug)

        if not self.category.is_published:
            raise Http404()

        return self.category.posts.filter(
            is_published=True,
            pub_date__lte=timezone.now()
        ).select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_object(self):
        return get_object_or_404(Post, id=self.kwargs['post_id'])

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.id})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/create.html'

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_object(self):
        return get_object_or_404(Post, id=self.kwargs['post_id'])


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("blog:post_detail", post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author != request.user:
        return redirect("blog:post_detail", post_id=comment.post.id)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect("blog:post_detail", post_id=comment.post.id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/comment.html', {
        'form': form,
        'comment': comment
    })


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author != request.user:
        return redirect("blog:post_detail", post_id=comment.post.id)

    context = {'comment': comment}
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=comment.post.id)
    return render(request, 'blog/comment.html', context=context)


def post_detail(request, post_id):
    template = 'blog/detail.html'
    post = get_object_or_404(
        Post.objects.select_related('category'),
        pk=post_id
    )

    if post.author != request.user and (
        not post.is_published
        or not post.category.is_published
        or post.pub_date > timezone.now()
    ):
        raise Http404()

    context = {
        'post': post,
        'form': CommentForm(),
        'comments': Comment.objects.filter(post=post).select_related('author')
    }
    return render(request, template, context)

# def index(request):
#     template = 'blog/index.html'
#     post_list = Post.objects.filter(
#         is_published=True,
#         category__is_published=True,
#         pub_date__lte=timezone.now()
#     ).select_related('category')[:5]
#     context = {'post_list': post_list}
#     return render(request, template, context)


# def category_posts(request, category_slug):
#     template = 'blog/category.html'
#     category = get_object_or_404(Category, slug=category_slug)
#     if not category.is_published:
#         raise Http404()
#     post_list = category.posts.filter(
#         is_published=True,
#         pub_date__lte=timezone.now()
#     ).select_related('category')

#     context = {'category': category,
#                'page_obj': post_list}
#     return render(request, template, context)
