from .models import Post    #, Comment
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PostForm
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import FormView

# django_filter
# from .filters import PostFilter
# 
# https://stackoverflow.com/questions/48872380/display-multiple-queryset-in-list-view
#  https://stackoverflow.com/questions/57234398/i-make-top-of-articles-but-when-i-start-my-project-i-had-error-unhashable-type
# pagination with filter ... FIXME
class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_context_data(self, *args, **kwargs):
        # context = super(PostListView, self).get_context_data(**kwargs)
        context = super().get_context_data(*args, **kwargs) #dict
        # context = self.get_queryset().values()
        # add additional object list
        context['featured'] = self.model.objects.all().filter(Q(featured=1) & Q(status=1)).order_by('date_posted')[:5]
        context['widgets']  = self.model.objects.all().filter(Q(category=1) & Q(status=1)).order_by('date_posted')[:5]

        # https://stackoverflow.com/questions/59972694/django-pagination-maintaining-filter-and-order-by
        get_copy = self.request.GET.copy()
        if get_copy.get('page'):
            get_copy.pop('page')
        context['get_copy'] = get_copy

        return context

    def get_queryset(self):
        try:
            keyword = self.request.GET['q']
        except:
            keyword = ''
        if (keyword != ''):
            object_list = self.model.objects.filter(
                Q(category=0) & Q(status=1) & ~Q(featured=1) &                 #published only, exclude featured..
                ( Q(content__icontains=keyword) | Q(title__icontains=keyword) ) )
        else:
            # object_list = self.model.objects.all()
            object_list = self.model.objects.filter(Q(category=0) & Q(status=1) & ~Q(featured=1))   #published only
        
        # breakpoint()
        if self.request.user.is_authenticated :   #not login
            return object_list
        else:
            return object_list.filter(private = False)


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post

    # def get_context_data(self, *args, **kwargs):
    #     context = self.get_object()
    #     context['md2'] = { 
    #         "content": markdown2.markdown(context.object.content),
    #         "title": context.object.title,
    #     }

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'image', 'category', 'featured', 'private', 'status', 'tags']
    # template_name = 'blog/post_form.html'
    success_url = '/'


# https://stackoverflow.com/questions/6989762/what-does-test-func-and-view-func-do-in-python-django
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'image', 'category', 'featured', 'private', 'status', 'tags']
    # template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_superuser or self.request.user.profile.is_psmadmin :
            return True
        return True if self.request.user == self.get_object().author else False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return True if self.request.user == self.get_object().author else False


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})


# @login_required
# def add_comment(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#     if request.method == 'POST':
#         user = User.objects.get(id=request.POST.get('user_id'))
#         text = request.POST.get('text')
#         Comment(author=user, post=post, text=text).save()
#         messages.success(request, "Your comment has been added successfully.")
#     else:
#         return redirect('post_detail', pk=pk)
#     return redirect('post_detail', pk=pk)
