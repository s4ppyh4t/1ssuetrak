""" == ISSUE VIEWS ==
- The code below provide user with endpoints to work with the Issue class/table 
icluding but not limitied to the following operations:
    + CRUD
    + Filter and Search
"""

# * Python base imports
import datetime
import time
# import pytz

# * Django imports
from django.contrib.messages import error, success
from django.db import DatabaseError, transaction
from django.db.models import Q, Prefetch, Count
from django.http import Http404, QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView

# * Issue app imports
from .models import Issue, IssueOwner, IssueComment
from .scripts.data_gen import IssueFactory
from .forms import issueCreateOrUpdateForm
from .forms import issueSortForm
from .forms import issueCommentForm
from .forms import IssueRecForm


#! >>> Base list view with pagination for issues:index <<< DONE
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
        query = Issue.objects.prefetch_related(Prefetch("o_uid", queryset=IssueOwner.objects.select_related("user"))).order_by("i_status",f"-{self.date_field}")
        if self.sort_option:
            query = query.order_by("-i_status", self.sort_option)

        if (self.filter_text is None) or (self.filter_text == ""):
            return query
        search_filter = Q(i_name__contains=self.filter_text)
        search_filter |= Q(i_desc__contains=self.filter_text)
        search_filter |= Q(i_desc__contains=self.filter_text)

        return query.filter(search_filter)


def index(request):
    context = {
        "title": "1ssues Board",
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
    # time.sleep(2)
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
    target_issue = get_object_or_404(Issue, pk=i_pk)
    context = {
        "issue": target_issue,
        "form": issueCreateOrUpdateForm(),
        "comments": IssueComment
                        .objects
                        .prefetch_related(
                            Prefetch(
                                "commenter",
                                queryset=IssueOwner.objects.select_related("user")
                            )
                        )
                        .filter(issue=i_pk)
                        .order_by("-c_date"),
        "ownership": request.user != target_issue.o_uid.user
    }
    return render(request, "issues/issue_detail.html", context=context)

#! >>> Call for solving the issue (form was included within the issue details template)
def solve_issue(request, i_pk):
    issue_obj = Issue.objects.get(pk=i_pk)
    if request.method != "POST":
        error(request, "Please use POST")
        return redirect(reverse("issues:issue_details", args=[i_pk]))
    
    if issue_obj.i_status:
        error(request, "Issue has already been solved")
        return redirect(reverse("issues:issue_details", args=[i_pk]))

    payload: QueryDict = request.POST.copy()
    payload.appendlist("s_uid", request.user)
    payload.appendlist("i_id", i_pk)

    form = IssueRecForm(payload)
    if not form.is_valid():
        error(request, form.errors)
    else:
        try:
            with transaction.atomic():
                solved_issue = form.save()
                issue_obj.i_status = True
                issue_obj.save()
            success(
                request,
                message=f"Issue #{ i_pk } has been solved @ { solved_issue.s_date }!",
            )
        except DatabaseError as e:
            error(request, f"Database error! {e}")
        except Exception as e:
            error(request, message=f"Something is wrong! {e}")
    
    return redirect(reverse("issues:issue_details", args=[i_pk]))





""" == ISSUE_OWNER VIEWS & ISSUE_COMMENT VIEWS ==
- The code below provide user with endpoints to work with the IssueOwner class/table 
icluding but not limitied to the following operations:
    + Creation (not including sign-up) / Read / Update (only avatar and name) / (No Deletion)

- For issue comments, the following views are also made to allow users to comment on Issues, 
as long as they are authenticated:
    + CR operations (no updates and delete, for fun :D)
"""
def owner_details(request, u_pk):
    issueOwner = IssueOwner.objects.prefetch_related("user").get(pk=u_pk)
    issueList = Issue.objects                           \
                    .prefetch_related("o_uid")          \
                    .filter(o_uid=u_pk)                 \
                    .order_by("-i_date", "-d_date")
    
    commentList = IssueComment.objects                  \
                              .prefetch_related(    
                                   Prefetch(
                                        'issue', 
                                        queryset=Issue.objects.select_related('o_uid')
                                        ))              \
                              .filter(commenter=u_pk)   \
                              .order_by("-c_date")
    
    look_range = 21

    analysis_data = { item['i_date__date'].strftime("%b-%d") : item["i_count"]  for item in list(issueList.filter(i_date__range=( datetime.datetime.today() - datetime.timedelta(days=look_range), datetime.datetime.today())).values("i_date__date").annotate(i_count=Count('pk')).values("i_date__date", "i_count").order_by("i_date__date")) }
    all_dates = [d.strftime("%b-%d") for d in (datetime.date.today() - datetime.timedelta(days=i) for i in range(look_range,-1,-1))]
    solve_data = { item['s_date__date'].strftime("%b-%d") : item["s_count"]  for item in list(issueOwner.issuerec_set.filter(s_date__range=( datetime.datetime.today() - datetime.timedelta(days=look_range), datetime.datetime.today())).values("s_date__date").annotate(s_count=Count('pk')).values("s_date__date", "s_count").order_by("s_date__date")) }

    context = {
        "issues": issueList,
        "comments": commentList,
        "user": issueOwner,
        "graph_data": {
            "i_date": all_dates,
            "i_count": [analysis_data.get(d, 0) for d in all_dates],
            "s_count": [solve_data.get(d, 0) for d in all_dates],
        }
    }

    return render(request, "issues/user_detail.html", context=context)


def create_comment(request, i_pk):
    issue_obj = Issue.objects.get(pk=i_pk)
    if request.method != "POST":
        error(request, "Please use POST")
        return redirect(reverse("issues:issue_details", args=[i_pk]))
    payload: QueryDict = request.POST.copy()

    payload.appendlist("commenter", request.user)
    payload.appendlist("issue", issue_obj)
    cmt_form = issueCommentForm(payload)

    if not cmt_form.is_valid():
        error(request, f"Something went wrong {cmt_form.errors}")
        print(cmt_form.errors)
    else:
        cmt_form.save()
    # return render(request, "issues/issue_comment.html")
    return redirect(reverse("issues:issue_details", args=[i_pk]))
