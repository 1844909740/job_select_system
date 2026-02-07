from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import OperationLog
from .serializers import OperationLogSerializer

class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OperationLogSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return OperationLog.objects.filter(user=self.request.user)
