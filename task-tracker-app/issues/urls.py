from django.urls import path

from . import views

app_name = "issues"

urlpatterns = [
    path("", views.index, name="index"),
    path("contains/", views.search_contains, name="search"),
    path("issue-details/<int:i_pk>/create-comment/", views.create_comment, name="create_comment"),
    path("issue-details/<int:i_pk>", views.get_issue_details, name="issue_details"),
    path("generate-issues/", views.generate_issues, name="generate_issues"),
    path("create-issue/", views.create_issue, name="create_issue"),
    path("delete-issue/", views.delete_issue, name="delete_issue"),
    path("user-details/<int:u_pk>", views.owner_details, name="user_details"),
    # path("detail-issue/<int:i_pk>", views.detail_issue, name="detail_issue"),
]
