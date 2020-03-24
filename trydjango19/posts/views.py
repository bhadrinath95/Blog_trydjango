from __future__ import unicode_literals
from urllib.parse import quote_plus 
from django.shortcuts import render, get_object_or_404, redirect
from django.http.response import HttpResponse, HttpResponseRedirect, Http404
from .models import Post
from .forms import PostForm
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q
from comments.models import Comment
from comments.forms import CommentForm
from django.contrib.contenttypes.models import ContentType
#from .utils import get_read_time

# Create your views here.
def posts_create(request): 
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    
    #if not request.user.is_authenticated():
        #raise  Http404
    
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit = False)
        instance.user = request.user
        instance.save()
        messages.success(request, "Successfully created")
        return HttpResponseRedirect(instance.get_absolute_url())
    
    """
    if request.method == 'POST':
        print (request.POST.get(title))
        print (request.POST.get(content))
        #title = request.POST.get(title)
        #Post.objects.create(title=title)
    """    
    context = {
            "form": form,
        }
    return render(request, 'post_form.html', context)

def posts_detail(request,id=None):
    #instance = Post.objects.get(id=1)
    instance = get_object_or_404(Post,id=id)
    if instance.draft or instance.publish > timezone.now().date():
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404
    share_string = quote_plus(instance.content)
    
    #print(get_read_time(instance.content))
    #print(get_read_time(instance.get_markdown()))
    initial_data = {
            "content_type": instance.get_content_type,
            "object_id": instance.id
        }
    
    form = CommentForm(request.POST or None, initial = initial_data)
    if form.is_valid() and request.user.is_authenticated:
        c_type = form.cleaned_data.get("content_type")
        content_type = ContentType.objects.get(model=c_type)
        obj_id = form.cleaned_data.get("object_id")
        content_data = form.cleaned_data.get("content")
        parent_obj = None
        try:
            parent_id = int(request.POST.get("parent_id"))
        except:
            parent_id = None
        
        if parent_id:
            parent_qs = Comment.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()
                
        new_comment, created = Comment.objects.get_or_create(
                            user = request.user,
                            content_type = content_type,
                            object_id = obj_id,
                            content = content_data,
                            parent = parent_obj,
                        )
        return HttpResponseRedirect(new_comment.content_object.get_absolute_url())
    
    #content_type = ContentType.objects.get_for_model(Post)
    #obj_id = instance.id
    comments = instance.comments #Comment.objects.filter_by_instance(instance)
    context = {
            "instance":instance,
            "title": "Detail",
            "share_string": share_string,
            "comments": comments,
            "comment_form": form,
        }
    return render(request, 'post_detail.html', context)

def posts_list(request):
    """
    if request.user.is_authenticated:
        context = {
            "title": "My user list"
        }
    else:
        context = {
            "title": "List"
        }
    """
    #queryset_list = Post.objects.filter(draft=False).filter(publish__lte=timezone.now())  #.all() #.order_by("-timestamp")
    
    today = timezone.now().date()
    
    queryset_list = Post.objects.active() #.all()
    
    if request.user.is_staff or request.user.is_superuser:
        queryset_list = Post.objects.all()
    
    query  = request.GET.get("query")
    if query:
        queryset_list = Post.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)            
            ).distinct()
    
    paginator = Paginator(queryset_list, 2) # Show 25 contacts per page.
    
    page_request_var = 'page'
    
    page = request.GET.get(page_request_var)
    
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)
        
    context = {
            "object_list": queryset,
            "title": "List",
            "page_request_var": page_request_var,
            "today": today,
        }
    return render(request, 'post_list.html', context)

def posts_update(request, id =None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post,id=id)
    
    form = PostForm(request.POST or None, request.FILES or None, instance = instance)
    
    if form.is_valid():
        instance = form.save(commit = False)
        instance.save()
        messages.success(request, "<a href='#'>Successfully</a> updated", extra_tags='Saved')
        return HttpResponseRedirect(instance.get_absolute_url())
        
    context = {
            "instance":instance,
            "title": instance.title,
            "form": form,
        }
    return render(request, 'post_form.html', context)

def posts_delete(request , id= None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post,id=id)
    instance.delete()
    messages.success(request, "Successfully Deleted")
    return redirect("posts:display")

