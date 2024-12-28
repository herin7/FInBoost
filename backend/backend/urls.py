# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import RegisterUserView,LogoutView
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/user/register/",RegisterUserView.as_view(), name = "register"),
    path("api-auth/logout/",RegisterUserView.as_view(), name = "register"),
    path("api/token/",TokenObtainPairView.as_view(), name = "get_token"),
    path("api/refresh/",TokenRefreshView.as_view(), name = "refresh"),
    path("api-auth/",include("rest_framework.urls")),
    path('api/', include('users.urls')),
    path('api/', include('finance.urls')),
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)