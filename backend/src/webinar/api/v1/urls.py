from django.urls import path

from . import views

urlpatterns = [
    path(
        'get_webinar/',
        views.WebinarView.as_view(),
        name='get_webinar'
    ),
]