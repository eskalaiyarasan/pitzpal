# Create your views here.
from django.shortcuts import render


def about_view(request):
    # You can pass data to the template via a dictionary (context)
    context = {
        "page_title": "About Page",
        "welcome_message": "Welcome to our About site!",
    }
    return render(request, "common/about.html", context)
