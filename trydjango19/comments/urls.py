from django.urls import path, re_path
from . import views


urlpatterns = [
    re_path('(?P<id>\d+)/delete/', views.comment_delete, name='delete'),  
    re_path('(?P<id>\d+)/', views.comment_thread, name = 'thread'), #\d - digit
     
]
