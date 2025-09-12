from django.urls import path, include

app_name = "v1"


urlpatterns = [
    path("entries", include("api.v1.entry.urls")),
]
