from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import (DetailView, ListView, UpdateView, CreateView,
                                  DeleteView)
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse

from .forms import CommentForm
from .models import Post, Category, User, Comment


def filter_posts(request):
    return request.filter(is_published=True,
                          category__is_published=True,
                          pub_date__lte=timezone.now())


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    current_time = timezone.now()

    if (post.pub_date > current_time
            or not post.is_published
            or not post.category.is_published):
        raise Http404()

    context = {
        'post': post,
        'form': CommentForm(),
        'comments': post.post_comment.all(),
    }

    return render(request, 'blog/detail.html', context)


class AuthorRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user != self.get_object().author:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)


class PostMixin:
    model = Post
    fields = ['title', 'text', 'pub_date', 'image', 'location', 'category']
    template_name = 'blog/create.html'


class CommentMixin:
    model = Comment
    fields = ['text']
    template_name = 'blog/comment.html'


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        current_time = timezone.now()

        queryset = super().get_queryset().filter(
            pub_date__lte=current_time,
            is_published=True,
            category__is_published=True,
        ).select_related('category')

        return queryset


class CategoryPostListView(ListView):
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']

        self.category = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )

        current_time = timezone.now()
        queryset = Post.objects.filter(
            category=self.category,
            pub_date__lte=current_time,
            is_published=True,
            category__is_published=True,
        ).select_related('category')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileListView(ListView):
    template_name = 'blog/profile.html'
    paginate_by = 5

    def get_queryset(self):
        username = self.kwargs['username']
        self.user = get_object_or_404(User, username=username)

        post_list = Post.objects.select_related(
            'category', 'location', 'author'
        ).filter(author__exact=self.user)

        if self.request.user != self.user:
            post_list = filter_posts(post_list)

        return post_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user
        return context


def logout_view(request):
    logout(request)
    return redirect('/')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ["first_name", "last_name", "username", "email"]
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


    def get_object(self):
        return self.request.user

class PostCreateView(PostMixin, LoginRequiredMixin, CreateView):
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(AuthorRequiredMixin, PostMixin, UpdateView):
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['pk']}
        )


class PostDeleteView(AuthorRequiredMixin, PostMixin, DeleteView):
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('blog:index')


class CommentCreateView(LoginRequiredMixin, CreateView, CommentMixin):
    form_class = CommentForm
    publication = None

    def dispatch(self, request, *args, **kwargs):
        self.publication = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.publication
        return super().form_valid(form)


    def get_queryset(self):
        return Comment.objects.filter(post=self.kwargs['post_id'])


class CommentUpdateView(AuthorRequiredMixin, UpdateView):
    model = Comment
    fields = ['text']
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_queryset(self):
        return Comment.objects.filter(post=self.kwargs['post_id'])


    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class CommentDeleteView(AuthorRequiredMixin, CommentMixin, DeleteView):
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})
