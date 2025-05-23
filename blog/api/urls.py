import debug_toolbar
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

import blog.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", blog.views.index),
    path("post/<slug>/", blog.views.post_detail, name="blog-post-detail"),
    path("ip/", blog.views.get_ip),
    
    # ✅ Include API URLs here
    path("api/", include("blog.api.urls")),

    # ✅ JWT Authentication endpoints
    path("jwt/", TokenObtainPairView.as_view(), name="jwt_obtain_pair"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt_refresh"),
]

# Add debug toolbar routes only in DEBUG mode
if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

# Optional: print the timezone setting
print(f"Time zone: {settings.TIME_ZONE}")
