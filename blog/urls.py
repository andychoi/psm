from django.urls import path
from . import views
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    UserPostListView,    
    # add_comment
)


urlpatterns = [
    path('',                        PostListView.as_view(), name='home'),
    path('user/<str:username>/',    UserPostListView.as_view(), name='user_posts'),
    path('post/new/',               PostCreateView.as_view(), name='post_create'),
    path("post/<slug:slug>/",       PostDetailView.as_view(), name="post_slug_detail"),  # new
    path('post/<int:pk>/update/',   PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/delete/',   PostDeleteView.as_view(), name='post_delete'),
    path('post/<int:pk>/',          PostDetailView.as_view(), name='post_detail'),
    path('about/', views.about, name='about'),
    # path('post/<int:pk>/comment/', add_comment, name='add_comment'),
]
