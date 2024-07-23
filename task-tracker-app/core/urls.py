from django.urls import path
from . import views


app_name='core'
urlpatterns = [
    path('', views.index, name="index"),
    path('gittab/git_retrieve', views.git_retrieve, name="git_retrieve"),
    path('gittab', views.git_tab, name="git_table"),
    # path('jobtab', views.job_tab, name="job_table")
]


