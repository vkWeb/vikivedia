from django.urls import path

from . import views

app_name = "encyclopedia"

urlpatterns = [
    path("", views.index, name="root"),
    path("wiki", views.wiki_redirect, name="wiki"),
    path("wiki/<str:title>", views.entry, name="wikititle"),
    path("new", views.new_entry, name="newentry"),
    path("random", views.random_entry, name="getrandomentry"),
    path("wiki/<str:title>/edit", views.edit_entry, name="editentry"),
    path("search", views.search, name="search"),
    path("delete-all-entries", views.delete_all_entries, name="deleteallentries")
]
