"""src/core/views.py."""

from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic import View

from src.shop.models import BankAccount
from src.shop.models import Product
from src.shop.models import TradeLog


class IndexView(TemplateView):
    """Render the main application page with DB data."""

    template_name = "core/index.html"

    def get_context_data(self, **kwargs):
        """Add products, account, and logs to the context."""
        context = super().get_context_data(**kwargs)
        context["products"] = Product.objects.all().order_by("id")
        context["account"] = BankAccount.objects.first()
        context["logs"] = TradeLog.objects.all()[:50]
        return context


class AuthActionView(View):
    """Handle both login and registration from the header form."""

    def post(self, request, *args, **kwargs):
        """Process authentication actions."""
        action = request.POST.get("action")
        username = request.POST.get("username")
        password = request.POST.get("password")

        if action == "register":
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password=password)
                login(request, user)
        elif action == "login":
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

        return redirect("core:index")


class UserLogoutView(LogoutView):
    """Handle user logout."""

    next_page = reverse_lazy("core:index")
