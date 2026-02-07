from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import AIAnalysisTask
from .serializers import AIAnalysisTaskSerializer

class AIAnalysisTaskViewSet(viewsets.ModelViewSet):
    serializer_class = AIAnalysisTaskSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return AIAnalysisTask.objects.filter(created_by=self.request.user)
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        task = self.get_object()
        task.status = '处理中'
        task.save()
        return Response({'message': f'任务 {task.title} 已开始执行'})
