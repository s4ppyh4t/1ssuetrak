""" == ISSUE VIEWS ==
- The code below provide user with endpoints to work with the Issue class/table 
icluding but not limitied to the following operations:
    + CRUD
    + Filter and Search
"""

# * Python base imports
import datetime

# import pytz

# * Django imports
from django.contrib.messages import error, success
from django.db import DatabaseError, IntegrityError, transaction
from django.db.models import F, Q
from django.http import Http404, QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView

# * Issue app imports
from .forms import issueCreateOrUpdateForm
from .models import Issue, IssueOwner
from .scripts.data_gen import IssueFactory
from .forms import issueSortForm


# todo >>> Base list view with pagination for issues:index <<<
class IssueListView(ListView):
    """
    Issue's ListView - subclass of Dj Generic Class-based View

    """

    paginate_by = 12
    queryset = None
    extra_context = {}
    date_field = "i_date"
    filter_text = None
    sort_option = None

    def get_context_data(self, **kwargs):
        context = super(IssueListView, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        return context

    def get_queryset(self):
        query = Issue.objects.all().order_by(f"-{self.date_field}")

        if self.sort_option:
            query = query.order_by(self.sort_option)

        if (self.filter_text is None) or (self.filter_text == ""):
            return query
        search_filter = Q(i_name__contains=self.filter_text)
        search_filter |= Q(i_desc__contains=self.filter_text)
        search_filter |= Q(i_desc__contains=self.filter_text)

        return query.filter(search_filter)


def index(request):
    context = {
        "currUser": request.user,
        "title": "Issues Board",
        "filter_text": None,
        "sort_form": issueSortForm(),
    }
    return IssueListView.as_view(
        template_name="issues/index.html",
        extra_context=context,
    )(request)


def search_contains(request):
    """Accept a filter text and pass it into :view:`issues.IssueListView`
    as a filter criteria to filter :model:`issues.Issue`
    """
    sort_option = request.GET.get("sort_option") or None
    filter_text = request.GET.get("filter_text") or None
    return IssueListView.as_view(
        template_name="issues/issue_tab.html",
        filter_text=filter_text,
        sort_option=sort_option,
        extra_context={"filter_text": filter_text},
    )(request)


#! >>> For dummy data generation <<< DONE
def generate_issues(request):
    """Generate dummy data for testing purposes. Will populate :model:`issues.Issue` records.
    Will rollback the saves/populations on database if error occurred

    Args:
        `request`: request accepted from user

    Returns:
        `HttpResponseRedirect`: A Django response object that redirect browser to index. Also carries a django `message` object to render pop-up/notification.
    """
    try:
        # Create a IssueFactory Faker batch that includes randomly generated data
        # which will then be saved via DjangoORM API
        batch_fake = IssueFactory.create_batch(100)
        with transaction.atomic():
            for issue in batch_fake:
                issue.save()

        # Return a success message if successful
        success(
            request,
            message="Successfully saved mock Issue data. Data are generated below",
        )
        # If an exception has occurred, generally catches the error and return an error message
    except DatabaseError as dbe:
        error(
            request,
            message=f"The site handled generation correctly, but the database did not: {dbe}",
        )
    except Exception as e:
        error(request, message=f"Error: {e}")

    # Send redirect to issues/index
    return redirect(reverse("issues:index"))


#!>>> For UpSert operations <<< DONE
def create_issue(request):
    if request.method != "POST":
        error("Incorrect method used! Please use POST method to create issues.")
        return redirect(reverse("issues:index"))

    # * Update and Clean input data from form for Form validation
    payload = request.POST.copy()
    payload.update(
        {
            "ugc_rating": int(payload.get("ugc_rating")),
            "dif_rating": int(payload.get("dif_rating")),
            "d_date": (
                datetime.datetime.fromisoformat(payload.get("d_date"))
                if payload.get("d_date")
                else None
            ),
            "o_uid": IssueOwner.objects.get(pk=request.user.id),
        }
    )

    issue_instance = None

    # * Check if this is an update or create request
    if request.POST.get("i_pk"):
        issue_instance = Issue.objects.get(pk=request.POST.get("i_pk"))

    # * Update to optionally update instance if exists
    new_issue_form = issueCreateOrUpdateForm(payload, instance=issue_instance)

    if not new_issue_form.is_valid():
        error(request, new_issue_form.errors)
        return redirect(reverse("issues:index"))
    try:
        with transaction.atomic():
            new_issue = new_issue_form.save()
        success(
            request,
            message=f"Issue #{ new_issue.pk } has been successfully {'updated' if issue_instance else 'created'}!",
        )
    except DatabaseError as e:
        error(request, f"Database error! {e}")
    except Exception as e:
        error(request, message=f"Something is wrong! {e}")

    return redirect(reverse("issues:index"))


#! >>> For Deletion <<< DONE
def delete_issue(request):
    """Delete an issue on POST request. POST payload accepts the following argument

    Payload Params:
        `i_pk` (int): DB Primary Key of the issue that user desired to delete.

    Returns:
        `HTTPResponseRedirect`: A redirect to issues/index, passing in the required "message"
    """
    if request.method != "POST":
        error(request, "Incorrect method used! Please use POST to delete issues!")
        return redirect(to=reverse("issues:index"))

    payload = request.POST
    try:
        target_issue = get_object_or_404(Issue, pk=payload.get("i_pk"))
        if target_issue.o_uid.pk != request.user.pk:
            error(
                request,
                f"You are not the owner of this issue ({target_issue.o_uid.user.username})",
            )
            return redirect(reverse("issues:index"))
        with transaction.atomic():
            target_issue.delete()
        success(request, f"Issue #{payload.get('i_pk')} successfully deleted")
    except (DatabaseError, Http404) as e:
        error(request, f"Something went wrong: {e}")

    return redirect(to=reverse("issues:index"))


#! >>> For detail gathering (possibly showing "update" page) DONE
def get_issue_details(request, i_pk):
    context = {
        "issue": get_object_or_404(Issue, pk=i_pk),
        # "model": Issue,
        "currUser": request.user,
        "form": issueCreateOrUpdateForm(),
    }
    return render(request, "issues/issue_detail.html", context=context)
