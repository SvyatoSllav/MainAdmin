from rest_framework import serializers
from .models import Webinar


class WebinarSerializer(serializers.ModelSerializer):

    class Meta:
        model = Webinar
        fields = ["title", "description", "web_format", "webinar_started_date"]
