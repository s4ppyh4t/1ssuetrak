from django.urls import path

from . import views

app_name = "issues"

urlpatterns = [
    path("", views.index, name="index"),
    path("contains/", views.search_contains, name="search"),
    path("issue-details/<int:i_pk>", views.get_issue_details, name="issue_details"),
    path("generate-issues/", views.generate_issues, name="generate_issues"),
    path("create-issue/", views.create_issue, name="create_issue"),
    path("delete-issue/", views.delete_issue, name="delete_issue"),
    # path("detail-issue/<int:i_pk>", views.detail_issue, name="detail_issue"),
]
