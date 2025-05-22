from rest_framework import generics, viewsets
from blog.models import Post
from blog.api.serializers import PostSerializer, UserSerializer
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer  # You probably want this here too

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            # Only published posts for anonymous users
            return self.queryset.filter(published_at__lte=timezone.now())
        if user.is_staff:
            # Staff users can see all posts
            return self.queryset
        # Regular users can see published posts or their own posts
        return self.queryset.filter(
            Q(published_at__lte=timezone.now()) | Q(author=user)
        )

    @method_decorator(cache_page(120))
    @method_decorator(vary_on_headers("Authorization", "Cookie"))
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)


class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class UserDetail(generics.RetrieveAPIView):
    lookup_field = "email"
    queryset = User.objects.all()
    serializer_class = UserSerializer
