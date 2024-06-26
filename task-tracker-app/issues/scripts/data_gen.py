import factory
import factory.django 
import factory.fuzzy
from issues.models import Issue, IssueOwner
import datetime


class IssueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Issue

    i_name = factory.Faker("sentence")
    i_desc = factory.Faker("sentence")
    i_date = factory.fuzzy.FuzzyNaiveDateTime(datetime.datetime(2024, 5, 1))
    d_date = factory.Iterator([datetime.datetime(2024, 6, 12), None])
    o_uid = factory.Iterator(IssueOwner.objects.all())
    ugc_rating = factory.Iterator(Issue.Rating_UGC.values)
    dif_rating = factory.Iterator(Issue.Rating_DIF.values)
