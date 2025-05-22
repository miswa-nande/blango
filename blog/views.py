
codio@financeariel-vocallemon:~/workspace$ python3 blango/manage.py runserver 0.0.0.0:8000
Watching for file changes with StatReloader
Performing system checks...

Exception in thread django-main-thread:
Traceback (most recent call last):
  File "/usr/lib/python3.6/threading.py", line 916, in _bootstrap_inner
    self.run()
  File "/usr/lib/python3.6/threading.py", line 864, in run
    self._target(*self._args, **self._kwargs)
  File "/home/codio/.local/lib/python3.6/site-packages/django/utils/autoreload.py", line 64, in wrapper
    fn(*args, **kwargs)
  File "/home/codio/.local/lib/python3.6/site-packages/django/core/management/commands/runserver.py", line 118, in inner_run
    self.check(display_num_errors=True)
  File "/home/codio/.local/lib/python3.6/site-packages/django/core/management/base.py", line 423, in check
    databases=databases,
  File "/home/codio/.local/lib/python3.6/site-packages/django/core/checks/registry.py", line 76, in run_checks
    new_errors = check(app_configs=app_configs, databases=databases)
  File "/home/codio/.local/lib/python3.6/site-packages/django/core/checks/urls.py", line 40, in check_url_namespaces_unique
    all_namespaces = _load_all_namespaces(resolver)
  File "/home/codio/.local/lib/python3.6/site-packages/django/core/checks/urls.py", line 57, in _load_all_namespaces
    url_patterns = getattr(resolver, 'url_patterns', [])
  File "/home/codio/.local/lib/python3.6/site-packages/django/utils/functional.py", line 48, in __get__
    res = instance.__dict__[self.name] = self.func(instance)
  File "/home/codio/.local/lib/python3.6/site-packages/django/urls/resolvers.py", line 598, in url_patterns
    patterns = getattr(self.urlconf_module, "urlpatterns", self.urlconf_module)
  File "/home/codio/.local/lib/python3.6/site-packages/django/utils/functional.py", line 48, in __get__
    res = instance.__dict__[self.name] = self.func(instance)
  File "/home/codio/.local/lib/python3.6/site-packages/django/urls/resolvers.py", line 591, in urlconf_module
    return import_module(self.urlconf_name)
  File "/usr/lib/python3.6/importlib/__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
  File "<frozen importlib._bootstrap>", line 994, in _gcd_import
  File "<frozen importlib._bootstrap>", line 971, in _find_and_load
  File "<frozen importlib._bootstrap>", line 955, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 665, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 678, in exec_module
  File "<frozen importlib._bootstrap>", line 219, in _call_with_frames_removed
  File "/home/codio/workspace/blango/blango/urls.py", line 18, in <module>
    import blog.views
  File "/home/codio/workspace/blango/blog/views.py", line 16, in <module>
    from blog.api.serializers import PostSerializer, TagSerializer, UserSerializer
ModuleNotFoundError: No module named 'blog.api'
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from blog.models import Post, Tag
from blog.forms import CommentForm

# New imports for API and caching
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers, vary_on_cookie

from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import viewsets, generics

from blog.api.serializers import PostSerializer, TagSerializer, UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

# Web views
def index(request):
    posts = Post.objects.filter(published_at__lte=timezone.now())
    return render(request, "blog/index.html", {"posts": posts})

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.user.is_active:
        if request.method == "POST":
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.content_object = post
                comment.creator = request.user
                comment.save()
                return redirect(request.path_info)
        else:
            comment_form = CommentForm()
    else:
        comment_form = None

    return render(
        request,
        "blog/post-detail.html",
        {
            "post": post,
            "comment_form": comment_form,
        },
    )

# API views
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @method_decorator(cache_page(300))
    @method_decorator(vary_on_headers("Authorization"))
    @method_decorator(vary_on_cookie)
    @action(methods=["get"], detail=False, name="Posts by the logged in user")
    def mine(self, request):
        if request.user.is_anonymous:
            raise PermissionDenied("You must be logged in to see which Posts are yours")
        posts = self.get_queryset().filter(author=request.user)
        serializer = PostSerializer(posts, many=True, context={"request": request})
        return Response(serializer.data)

    @method_decorator(cache_page(120))
    def list(self, *args, **kwargs):
        return super(PostViewSet, self).list(*args, **kwargs)


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @method_decorator(cache_page(300))
    def get(self, *args, **kwargs):
        return super(UserDetail, self).get(*args, **kwargs)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    @method_decorator(cache_page(300))
    def list(self, *args, **kwargs):
        return super(TagViewSet, self).list(*args, **kwargs)

    @method_decorator(cache_page(300))
    def retrieve(self, *args, **kwargs):
        return super(TagViewSet, self).retrieve(*args, **kwargs)
