from django.urls import path, re_path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.posts_list, name='display'),
    path('create', views.posts_create),
    #re_path('(?P<slug>\w+)/edit/', views.posts_update, name = 'update'),
    re_path('(?P<id>\d+)/edit/', views.posts_update, name = 'update'),
    re_path('(?P<id>\d+)/delete/', views.posts_delete),
    re_path('(?P<id>\d+)',views.posts_detail,name='detail'),
    
]
