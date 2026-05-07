# Create your views here.
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import CustomUserCreationForm
from .models import FriendRequest, Friends, User


def signup_view(request, *args, **kwargs):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after signup
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


def search_users(request):
    query = request.GET.get("q")
    results = []

    if query:
        results = User.objects.filter(username__icontains=query).exclude(
            id=request.user.id
        )

    return render(request, "social/search.html", {"results": results})


# views.py


def friend_requests(request):
    # Change 'accepted' to 'is_accepted' to match your model
    requests = FriendRequest.objects.filter(to_user=request.user, is_accepted=False)
    return render(request, "social/requests.html", {"requests": requests})


def send_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)

    # Use get_or_create or a safety check to prevent the crash for existing users
    user_friends, created = Friends.objects.get_or_create(user=request.user)

    if request.user == to_user:
        pass
    elif to_user in user_friends.friends_list.all():
        pass
    elif not FriendRequest.objects.filter(
        from_user=request.user, to_user=to_user
    ).exists():
        FriendRequest.objects.create(from_user=request.user, to_user=to_user)

    return redirect("search")


def accept_request(request, request_id):
    fr = FriendRequest.objects.get(id=request_id)

    if not fr.is_accepted:
        fr.is_accepted = True
        fr.status = "accepted"
        fr.save()

        sender_friends = fr.from_user.friends_obj
        receiver_friends = fr.to_user.friends_obj

        sender_friends.friends_list.add(fr.to_user)
        receiver_friends.friends_list.add(fr.from_user)
    return redirect("friends_list")


def reject_request(request, request_id):
    fr = get_object_or_404(FriendRequest, id=request_id)

    if fr.to_user == request.user:
        fr.delete()

    return redirect("friends_list")


def friends_list(request):
    friends = request.user.friends_obj.friends_list.all()
    return render(request, "social/friends.html", {"friends": friends})


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # This creates the session
            return Response(
                {"detail": "Successfully logged in."}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response(
            {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
        )


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("username", "password", "dob", "ph", "email")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        # We use create_user to ensure the password gets hashed correctly!
        return User.objects.create_user(**validated_data)
