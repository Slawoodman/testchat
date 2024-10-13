from rest_framework.response import Response
from .models import Message, Thread
from rest_framework import viewsets, status
from .api.serializers import ReadMarkSerializer, MessageSerializer, ThreadSerializer
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.decorators import action
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm


def index(request):
    return render(request, "chat/index.html")


def login_user(request):
    page = "login"
    if request.user.is_authenticated:
        messages.error(request, "You already logged in")
        return redirect("chat:index")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(
                request, "The user is not found. Pls enter the right username"
            )
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, "You logged in!")
                return redirect("chat:index")
            else:
                messages.error(request, "Disabled account")
        else:
            messages.error(request, "The password is incorrect")
    return render(request, "login_register.html", {"page": page})


def register_user(request):
    context = {}
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            user = User.objects.create_user(username=username, password=password)
            messages.success(request, "Account is created!")
            login(request, user)
            return redirect("chat:index")
    else:
        form = UserCreationForm()
    context["form"] = form
    return render(request, "login_register.html", context)


def logout_user(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect("chat:index")


class ThreadViewSet(viewsets.ModelViewSet):
    serializer_class = ThreadSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAuthenticated]
    queryset = Thread.objects.all()

    def retrieve(self, request, pk=None):
        thread = get_object_or_404(Thread, pk=pk)
        if request.user in thread.participants.all():
            serializer = ThreadSerializer(thread)
            return Response(serializer.data)
        else:
            return Response("Not allowed", status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def list(self, request):
        user = request.user
        threads = Thread.objects.filter(participants=user)
        pagination = self.pagination_class()
        result_page = pagination.paginate_queryset(threads, request)
        serializer = ThreadSerializer(result_page, many=True)
        return pagination.get_paginated_response(serializer.data)

    def create(self, request):
        serializer = ThreadSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            participants = serializer.validated_data["participants"]
            if len(participants) != 2:
                return Response(
                    {"detail": "A thread must have exactly two participants."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            existing_thread = (
                Thread.objects.filter(participants__in=participants)
                .distinct()
                .annotate(count=Count("participants"))
                .filter(count=2)
                .first()
            )

            if existing_thread:
                existing_serializer = ThreadSerializer(existing_thread)
                return Response(
                    {
                        "detail": "An existing thread was found.",
                        "thread": existing_serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            existing_serializer = serializer.save()
            return Response(
                {
                    "detail": "An thread was created.",
                    "thread": existing_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        thread = get_object_or_404(Thread, pk=pk)
        if request.user in thread.participants.all():
            thread.delete()
            return Response(
                {"detail": "Thread is successfully deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        else:
            return Response(
                {"detail": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
            )


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        id_of_thread = self.request.query_params.get("thread_id")
        if id_of_thread:
            return self.queryset.filter(
                thread_id=id_of_thread, thread__participants=self.request.user
            )
        return self.queryset.exclude(sender=self.request.user, is_read=False)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.context["request"] = request
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        thread = message.thread
        thread.updated = timezone.now()
        thread.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=("post", "get"))
    def mark_as_read(self, request, pk=None):
        message = self.get_object()
        serializer = ReadMarkSerializer(message, data={"is_read": True}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": "message marked as read"})

    @action(detail=False, methods=["get"])
    def unread(self, request):
        count = (
            Message.objects.filter(is_read=False).exclude(sender=request.user).count()
        )
        return Response({"unread_count": count})
