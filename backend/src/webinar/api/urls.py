from django.urls import path, include

urlpatterns = [
    path('v1/', include('src.webinar.api.v1.urls'))
]
