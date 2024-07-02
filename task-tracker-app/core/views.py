# Python's utilities
from result import Ok, Err, Result

# Django dependencies
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction
from django.http import HttpResponseNotFound
from django.contrib.messages import success, error

# customer imports
from core.forms import SignupForm, IssueOwnerForm
from .scripts.git_commit_parser import scrape_commits
from issues.models import IssueOwner


# Create your views here.
def index(request):
    return render(
        request,
        "core/index.html",
        {"currUser": request.user, "title": "1ssuetrak Home"},
    )


def git_tab(request):
    app_name = "1ssuetrak"
    data: Result[dict, str] = scrape_commits(
        url=f"https://api.github.com/repos/s4ppyh4t/{app_name}/commits"
    )
    payload: list
    if data.is_ok():
        payload = data.ok_value

    return render(
        request,
        "core/git_table.html",
        {
            "data": list(payload.items()),
            "currUser": request.user,
        },
    )


# ! Authentication views
def auth_signup(request):
    return render(
        request,
        "registration/signup_bs.html",
        {"currUser": request.user, "form": None, "is_filled": False, "owner_form": IssueOwnerForm()},
    )


@transaction.atomic
def api_createuser(request):
    # SignupForm
    payload = request.POST.copy()
    if request.method == "POST":
        form = SignupForm(payload)
        print(payload)
        print(request.FILES)
        if form.is_valid():
            # Save the user created from the form
            try:
                u = form.save()

                # prepare for issueowner creation
                payload.appendlist("user", u)
                ownerForm = IssueOwnerForm(payload, request.FILES)
                if not ownerForm.is_valid():
                    raise Exception("something is wrong")
                ownerForm.save()
                success(request, f"User {u.username} has been saved successfully")
            except Exception as e:
                error(request, f"An error has occured: {e}")
        else:
            # Return for validation of forms
            return render(
                request,
                "registration/signup_bs.html",
                {"form": form, "currUser": request.user, "is_filled": True},
            )
    else:
        form = SignupForm()
        form.add_error(error="Do not use GET to create an user!")
        # Return if incorrectly requested
        return render(
            request,
            "registration/signup_bs.html",
            {"form": form, "currUser": request.user, "is_filled": True},
        )

    return redirect(to=reverse("core:index"))
