from django.contrib.auth import login, views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.urls import path

from navigation import PLACE_LIST, route_map
from pipeline import graph

MEMORY = 5  # question-answer pairs remembered per user


def signup(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        login(request, form.save())
        return redirect("chat")
    return render(request, "form.html", {"form": form, "title": "Sign up"})


@login_required
def chat(request):
    history = request.session.get("history", [])
    query = request.POST.get("query", "").strip()
    if query:
        answer = graph.invoke({"query": query, "history": history})["final"]
        request.session["history"] = (history + [[query, answer]])[-MEMORY:]
        return redirect("chat")  # so refreshing the page doesn't resend the question
    return render(request, "chat.html", {"history": history})


@login_required
def navigation(request):
    context = {"places": PLACE_LIST, "start": request.GET.get("start", ""), "end": request.GET.get("end", "")}
    if context["start"] and context["end"]:
        try:
            context["start"], context["end"], context["info"], context["map_html"] = route_map(
                context["start"], context["end"]
            )
        except ValueError as e:
            context["error"] = str(e)
    return render(request, "navigation.html", context)


urlpatterns = [
    path("", chat, name="chat"),
    path("navigation/", navigation, name="navigation"),
    path("signup/", signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="form.html", extra_context={"title": "Login"}), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
