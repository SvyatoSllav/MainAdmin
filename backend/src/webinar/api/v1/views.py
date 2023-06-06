from rest_framework.views import APIView
from rest_framework.response import Response
from src.webinar.models import Webinar
from src.webinar.serializer import WebinarSerializer


class WebinarView(APIView):
    def get(self, request):
        """
        Get's webinar from db.
        """
        try:
            webinar = Webinar.objects.order_by("webinar_started_date").first()
            serializer = WebinarSerializer(webinar)
            return Response(serializer.data)
        except Exception as e:
            print(e)
