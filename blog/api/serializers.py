from rest_framework import serializers
from blog.models import Post, Tag
from django.contrib.auth.models import User
from versatileimagefield.serializers import VersatileImageFieldSerializer

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
    
    hero_image = VersatileImageFieldSerializer(
        sizes=[
            ("full_size", "url"),
            ("thumbnail", "thumbnail__100x100"),
        ],
        read_only=True,
    )

    class Meta:
        model = Post
        exclude = ["ppoi"]
        read_only_fields = ["modified_at", "created_at"]

class PostDetailSerializer(PostSerializer):
    hero_image = VersatileImageFieldSerializer(
        sizes=[
            ("full_size", "url"),
            ("thumbnail", "thumbnail__100x100"),
            ("square_crop", "crop__200x200"),
        ],
        read_only=True,
    )
