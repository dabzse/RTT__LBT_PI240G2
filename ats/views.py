from django.shortcuts import render
from django.db.models.query import QuerySet

# Create your views here.
def home(request):
    return render(request, "ats/home.html", {})
