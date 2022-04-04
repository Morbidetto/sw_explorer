from django.urls import path

from characters.views import (
    CharactersListView,
    CharactersDetailView,
    download_characters,
)

app_name = "characters"

urlpatterns = [
    path("", CharactersListView.as_view(), name="characters-list"),
    path("download/", download_characters, name="download-characters"),
    path("<int:pk>/", CharactersDetailView.as_view(), name="characters-detail"),
]
