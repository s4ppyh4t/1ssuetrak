from django.contrib import admin
from .models import IssueOwner, IssueRec, Issue, IssueComment
# Register your models here.
admin.site.register([IssueOwner, IssueRec, Issue, IssueComment])