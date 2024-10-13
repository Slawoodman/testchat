from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

app_name = "chat"

router = DefaultRouter()
router.register(r"threads", views.ThreadViewSet)
router.register(r"messages", views.MessageViewSet)


urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("register/", views.register_user, name="register"),
    path("api/", include(router.urls)),
]
