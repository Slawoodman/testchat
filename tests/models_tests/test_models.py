from django.utils import timezone
import pytest
from chat.models import Thread
from django.contrib.auth.models import User


@pytest.mark.django_db
class Test_Models:
    @pytest.fixture
    def create_user(db):
        def _create_user(username, email, password):
            return User.objects.create(
                username=username, email=email, password=password
            )

        return _create_user

    def test_user_creating(self, create_user):
        create_user(username="testUser", email="testgmail.com", password="1234")
        assert User.objects.all().count() == 1

    def test_thread_creating(self, create_user):
        user1 = create_user(username="testUser", email="testgmail.com", password="1234")
        user2 = create_user(username="testser", email="testgmail.com", password="1234")
        thread = Thread.objects.create(created=timezone.now(), updated=timezone.now())
        thread.participants.set([user1, user2])
        assert Thread.objects.all().count() == 1
