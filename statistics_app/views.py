from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from position_data.models import Position
from .models import StatisticsReport, IndustryStatistics, SalaryStatistics
from .serializers import StatisticsReportSerializer, IndustryStatisticsSerializer, SalaryStatisticsSerializer

class StatisticsReportViewSet(viewsets.ModelViewSet):
    serializer_class = StatisticsReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return StatisticsReport.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate_industry_report(self, request):
        industry = request.data.get('industry')
        positions = Position.objects.filter(industry=industry)
        if not positions.exists():
            return Response({'error': '未找到该行业的数据'}, status=status.HTTP_404_NOT_FOUND)
        
        stats = positions.aggregate(total=Count('id'))
        top_companies = list(positions.values('company').annotate(count=Count('id')).order_by('-count')[:10])
        result_data = {'industry': industry, 'total_positions': stats['total'], 'top_companies': top_companies}
        
        report = StatisticsReport.objects.create(
            title=f'{industry}行业分析报告',
            report_type='行业分析',
            parameters={'industry': industry},
            result_data=result_data,
            created_by=request.user
        )
        return Response(StatisticsReportSerializer(report).data)

class IndustryStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IndustryStatistics.objects.all()
    serializer_class = IndustryStatisticsSerializer
    permission_classes = [IsAuthenticated]

class SalaryStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SalaryStatistics.objects.all()
    serializer_class = SalaryStatisticsSerializer
    permission_classes = [IsAuthenticated]
