from rest_framework import generics
from blango_auth.models import User
from blog.api.serializers import UserSerializer, PostSerializer  # Ensure both are imported

class UserDetail(generics.RetrieveAPIView):
    lookup_field = "email"
    queryset = User.objects.all()
    serializer_class = UserSerializer
