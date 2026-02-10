"""
统计分析视图 - 支持按关键词/意向岗位筛选
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Q
from position_data.models import Position, PositionQuery, FavoritePosition
from .models import StatisticsReport, IndustryStatistics, SalaryStatistics
from .serializers import StatisticsReportSerializer, IndustryStatisticsSerializer, SalaryStatisticsSerializer


class StatisticsReportViewSet(viewsets.ModelViewSet):
    serializer_class = StatisticsReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StatisticsReport.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class IndustryStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IndustryStatistics.objects.all()
    serializer_class = IndustryStatisticsSerializer
    permission_classes = [IsAuthenticated]


class SalaryStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SalaryStatistics.objects.all()
    serializer_class = SalaryStatisticsSerializer
    permission_classes = [IsAuthenticated]


# ====================== 辅助函数 ======================

def _get_filtered_positions(request):
    """根据 query-string 过滤 Position 集合
    ?keyword=Python       按标题/公司搜索
    ?scope=favorites      只看意向（收藏）岗位
    """
    keyword = request.query_params.get('keyword', '').strip()
    scope = request.query_params.get('scope', 'all')

    qs = Position.objects.all()
    if scope == 'favorites':
        fav_ids = FavoritePosition.objects.filter(
            user=request.user
        ).values_list('position_id', flat=True)
        qs = qs.filter(id__in=fav_ids)

    if keyword:
        qs = qs.filter(Q(title__icontains=keyword) | Q(company__icontains=keyword))

    return qs


def _parse_avg_salary(salary_range_str):
    """解析 '15-25K' → 20.0"""
    try:
        parts = salary_range_str.replace('K', '').replace('k', '').split('-')
        return (int(parts[0]) + int(parts[1])) / 2
    except:
        return None


# ====================== API 端点 ======================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def basic_statistics(request):
    """概览统计"""
    qs = _get_filtered_positions(request)
    total = qs.count()
    companies = qs.values('company').distinct().count()
    cities = qs.values('location').distinct().count()

    salaries = []
    for sr in qs.values_list('salary_range', flat=True)[:3000]:
        v = _parse_avg_salary(sr)
        if v:
            salaries.append(v)
    avg_salary = round(sum(salaries) / len(salaries), 1) if salaries else 0

    return Response({
        'total_positions': total,
        'avg_salary': avg_salary,
        'total_companies': companies,
        'total_cities': cities,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def salary_distribution(request):
    """薪资分布"""
    qs = _get_filtered_positions(request)
    buckets = [
        ('5K以下', 0, 5), ('5-10K', 5, 10), ('10-15K', 10, 15),
        ('15-20K', 15, 20), ('20-30K', 20, 30), ('30-50K', 30, 50),
        ('50K以上', 50, 999),
    ]
    counts = {label: 0 for label, _, _ in buckets}
    for sr in qs.values_list('salary_range', flat=True).iterator():
        avg = _parse_avg_salary(sr)
        if avg is None:
            continue
        for label, lo, hi in buckets:
            if lo <= avg < hi:
                counts[label] += 1
                break
    return Response([{'name': l, 'value': counts[l]} for l, _, _ in buckets])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def experience_distribution(request):
    qs = _get_filtered_positions(request)
    data = qs.values('experience').annotate(count=Count('id')).order_by('-count')
    return Response([{'name': d['experience'], 'value': d['count']} for d in data])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def education_distribution(request):
    qs = _get_filtered_positions(request)
    data = qs.values('education').annotate(count=Count('id')).order_by('-count')
    return Response([{'name': d['education'], 'value': d['count']} for d in data])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def position_type_distribution(request):
    qs = _get_filtered_positions(request)
    data = qs.values('position_type').annotate(count=Count('id')).order_by('-count')
    return Response([{'name': d['position_type'], 'value': d['count']} for d in data])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def city_distribution(request):
    qs = _get_filtered_positions(request)
    data = qs.values('location').annotate(count=Count('id')).order_by('-count')[:10]
    return Response([{'name': d['location'], 'value': d['count']} for d in data])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def industry_distribution(request):
    qs = _get_filtered_positions(request)
    data = qs.values('industry').annotate(count=Count('id')).order_by('-count')[:10]
    return Response([{'name': d['industry'], 'value': d['count']} for d in data])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def company_distribution(request):
    """热门公司 Top10"""
    qs = _get_filtered_positions(request)
    data = qs.values('company').annotate(count=Count('id')).order_by('-count')[:10]
    return Response([{'name': d['company'], 'value': d['count']} for d in data])
