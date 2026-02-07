from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import ChartComponent
from .serializers import ChartComponentSerializer

class ChartComponentViewSet(viewsets.ModelViewSet):
    serializer_class = ChartComponentSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return ChartComponent.objects.filter(created_by=self.request.user)
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
