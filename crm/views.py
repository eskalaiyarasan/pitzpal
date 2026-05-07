# Create your views here.
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.shortcuts import redirect, render
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import CustomUserCreationForm


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
