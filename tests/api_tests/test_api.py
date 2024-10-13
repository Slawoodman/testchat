from django.utils import timezone
import pytest
from chat.models import Thread
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse


@pytest.mark.django_db
class Test_Api:
    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def create_user(self):
        def _create_user(username, password):
            return User.objects.create_user(username=username, password=password)

        return _create_user

    @pytest.fixture
    def thread_obj(self, create_user):
        user = create_user("testuser", "password")
        user1 = create_user("test", "password")

        thread = Thread.objects.create(created=timezone.now(), updated=timezone.now())
        thread.participants.set([user, user1])
        return thread

    @pytest.fixture
    def authenticated_user(self, client):
        def authentication(user):
            client.force_authenticate(user)

        return authentication

    @pytest.fixture
    def threads_url(self):
        return reverse("chat:thread-list")

    @pytest.fixture
    def thread_url(self, thread_obj):
        return reverse("chat:thread-detail", kwargs={"pk": thread_obj.pk})

    def test_get_threads(self, client, authenticated_user, create_user, threads_url):
        user = create_user(username="GetUserPosts", password="password")
        authenticated_user(user)
        response = client.get(threads_url)
        assert response.status_code == status.HTTP_200_OK

    def test_get_thread_denied(
        self, create_user, client, authenticated_user, thread_url
    ):
        user = create_user(username="GetUserPosts", password="password")
        authenticated_user(user)
        response = client.get(thread_url)
        assert response.status_code == 405

    def test_delete_post(self, client, authenticated_user, thread_url):
        user = User.objects.get(username="testuser")
        authenticated_user(user)
        response = client.delete(thread_url)
        assert Thread.objects.all().count() == 0
        assert response.status_code == status.HTTP_204_NO_CONTENT
