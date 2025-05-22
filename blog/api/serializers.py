from rest_framework import serializers
from blog.models import Post, Tag
<<<<<<< HEAD
from django.contrib.auth import get_user_model

User = get_user_model()

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
=======
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

class PostSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        slug_field="value",
        many=True,
        queryset=Tag.objects.all()
    )

    author = serializers.HyperlinkedRelatedField(
        queryset=User.objects.all(),
        view_name="api_user_detail",
        lookup_field="email"
    )

    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = ["modified_at", "created_at"]
>>>>>>> 467cdd6deee058e2f719d5f4bd79c1dc2763ed8f
