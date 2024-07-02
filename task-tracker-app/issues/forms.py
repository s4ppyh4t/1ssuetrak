from django import forms
# from django.db import models

from .models import Issue
from .models import IssueComment

# from crispy_bootstrap5 import


class issueCreateOrUpdateForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ["i_name", "i_desc", "ugc_rating", "dif_rating", "d_date", "o_uid"]


class issueSortForm(forms.Form):
    SORT_OPTIONS = (
        ("i_name", "Name"),
        ("-i_date", "Issued dates (closest first)"),
        ("i_date", "Issued dates (furthest first)"),
        ("-d_date", "Deadline dates (furthest first)"),
        ("d_date", "Deadline dates (closest first)"),
        ("ugc_rating", "Urgency (low to high)"),
        ("-ugc_rating", "Urgency (high to low)"),
        ("dif_rating", "Difficulty (low to high)"),
        ("-dif_rating", "Difficulty (high to low)"),
    )
    sort_option = forms.ChoiceField(choices=SORT_OPTIONS)

class issueCommentForm(forms.ModelForm):
    class Meta:
        model = IssueComment
        fields = {"commenter", "issue", "c_cont"}