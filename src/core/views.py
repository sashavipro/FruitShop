"""src/core/views.py."""

from django.shortcuts import render

def index_view(request):
    """Render the main application page."""
    return render(request, "core/index.html")