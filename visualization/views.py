from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ChartComponent, Dashboard
from .serializers import ChartComponentSerializer, DashboardSerializer

class DashboardViewSet(viewsets.ModelViewSet):
    """仪表盘视图集"""
    serializer_class = DashboardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Dashboard.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """预览仪表盘"""
        dashboard = self.get_object()
        serializer = DashboardSerializer(dashboard)
        return Response(serializer.data)


class ChartComponentViewSet(viewsets.ModelViewSet):
    """图表组件视图集"""
    serializer_class = ChartComponentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChartComponent.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def test_data(self, request, pk=None):
        """测试图表数据"""
        chart = self.get_object()
        # 生成模拟数据用于测试
        mock_data = {
            'xAxis': ['一月', '二月', '三月', '四月', '五月', '六月'],
            'series': [
                {
                    'name': '数据1',
                    'data': [120, 132, 101, 134, 90, 230]
                },
                {
                    'name': '数据2',
                    'data': [220, 182, 191, 234, 290, 330]
                }
            ]
        }
        return Response(mock_data)
    
    @action(detail=True, methods=['post'])
    def add_to_dashboard(self, request, pk=None):
        """添加图表到仪表盘"""
        chart = self.get_object()
        dashboard_id = request.data.get('dashboard_id')
        
        if not dashboard_id:
            return Response({'error': '缺少仪表盘ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            dashboard = Dashboard.objects.get(id=dashboard_id, created_by=request.user)
            chart.dashboard = dashboard
            chart.save()
            return Response({'message': '图表已添加到仪表盘'})
        except Dashboard.DoesNotExist:
            return Response({'error': '仪表盘不存在'}, status=status.HTTP_404_NOT_FOUND)
