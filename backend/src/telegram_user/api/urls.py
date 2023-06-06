from django.urls import path, include

urlpatterns = [
    path('v1/', include('src.telegram_user.api.v1.urls'))
]