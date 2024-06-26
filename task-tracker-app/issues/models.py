import datetime

import pytz
from django.contrib.auth.models import User
from django.db import models
# from django.db.models.functions import Now
from django.utils import timezone
# from django.utils.translation import gettext_lazy as _
# from faker import Faker, factory


# Create your models here.
class Issue(models.Model):

    # Enumeration Types
    class Rating_UGC(models.IntegerChoices):
        MISC = 1
        NON_UGN = 2
        ESSENTIAL = 3
        UGN = 4
        HIGH_UGN = 5

    class Rating_DIF(models.IntegerChoices):
        VERY_EASY = 1
        EASY = 2
        MEDIUM = 3
        HARD = 4
        VERY_HARD = 5

    i_name = models.CharField(max_length=50, default="New Issue")
    i_desc = models.CharField(max_length=512, default="No desc", blank=True)
    ugc_rating = models.IntegerField(
        default=Rating_UGC.MISC, choices=Rating_UGC.choices
    )
    dif_rating = models.IntegerField(
        default=Rating_DIF.EASY, choices=Rating_DIF.choices
    )
    i_date = models.DateTimeField(verbose_name="issue_date", default=timezone.now)
    s_date = models.DateTimeField(verbose_name="solved_date", blank=True, null=True)
    d_date = models.DateTimeField(verbose_name="deadline", blank=True, null=True)
    o_uid = models.ForeignKey(
        to="IssueOwner", on_delete=models.PROTECT, related_name="owner_uid", default=2
    )
    i_status = models.BooleanField(
        default=False,
        choices=((False, "Not solved"), (True, "Solved")),
        verbose_name="Solve status",
    )

    def __str__(self):
        return f"{self.i_name} - {self.i_date.strftime('%d/%m/%y @ %H:%M')} [{self.get_i_status_display()}]"

    def created_recently(self):
        return datetime.datetime.now(
            tz=pytz.timezone("Australia/Melbourne")
        ) - datetime.datetime(self.i_date) <= datetime.timedelta(days=2)

    def get_ugc_choices(self):
        field = self.ugc_rating.choices
        return field


class IssueRec(models.Model):
    i_id = models.ForeignKey(to="Issue", on_delete=models.PROTECT, default=2)
    s_uid = models.ForeignKey(
        to="IssueOwner",
        on_delete=models.SET_NULL,
        null=True,
        related_name="solver_uid",
        default=2,
    )
    i_cost = models.FloatField(max_length=50, verbose_name="issue_cost", default=0.0)

    def __str__(self):
        return f"Issue {self.i_id} owned by {self.o_uid} - resolved by {self.s_uid}"


class IssueOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    pts = models.IntegerField(default=0, verbose_name="UserPoints")

    def __str__(self):
        return f"{self.user.pk} - {self.user.username}: {self.pts} points"
