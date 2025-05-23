from rest_framework import generics, viewsets
from blog.models import Post
from blog.api.serializers import PostSerializer, UserSerializer
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from datetime import timedelta
from django.http import Http404


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            queryset = self.queryset.filter(published_at__lte=timezone.now())
        elif user.is_staff:
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(
                Q(published_at__lte=timezone.now()) | Q(author=user)
            )

        # Handle optional time period filter
        time_period_name = self.kwargs.get("period_name")
        if not time_period_name:
            return queryset

        if time_period_name == "new":
            return queryset.filter(published_at__gte=timezone.now() - timedelta(hours=1))
        elif time_period_name == "today":
            return queryset.filter(published_at__date=timezone.now().date())
        elif time_period_name == "week":
            return queryset.filter(published_at__gte=timezone.now() - timedelta(days=7))
        else:
            raise Http404(
                f"Time period '{time_period_name}' is not valid, should be 'new', 'today', or 'week'."
            )

    @method_decorator(cache_page(120))
    @method_decorator(vary_on_headers("Authorization", "Cookie"))
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)


class PostList(generics.ListCreateAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return Post.objects.filter(published_at__lte=timezone.now())
        if user.is_staff:
            return Post.objects.all()
        return Post.objects.filter(
            Q(published_at__lte=timezone.now()) | Q(author=user)
        )


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return Post.objects.filter(published_at__lte=timezone.now())
        if user.is_staff:
            return Post.objects.all()
        return Post.objects.filter(
            Q(published_at__lte=timezone.now()) | Q(author=user)
        )


class UserDetail(generics.RetrieveAPIView):
    lookup_field = "email"
    queryset = User.objects.all()
    serializer_class = UserSerializer