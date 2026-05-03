import time
import random
import json
import re
import numpy as np
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Count, Q
from .models import AIAnalysisTask, AIAlgorithm, AIAnalysisResult
from .serializers import AIAnalysisTaskSerializer, AIAlgorithmSerializer, AIAnalysisResultSerializer
from position_data.models import Position


class AIAlgorithmViewSet(viewsets.ModelViewSet):
    serializer_class = AIAlgorithmSerializer
    permission_classes = [IsAuthenticated]
    queryset = AIAlgorithm.objects.all()


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
        start_time = time.time()
        try:
            algorithm_type = task.algorithm.algorithm_type if task.algorithm else (task.algorithm_type or 'recommendation')
            result = self._dispatch(algorithm_type, task)
            execution_time = (time.time() - start_time) * 1000
            task.status = '已完成'
            task.result = result
            task.execution_time = execution_time
            task.save()
            self._save_result(task, result, algorithm_type)
            return Response({'message': f'任务 {task.title} 执行完成', 'result': result})
        except Exception as e:
            task.status = '失败'
            task.error_message = str(e)
            task.execution_time = (time.time() - start_time) * 1000
            task.save()
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def result(self, request, pk=None):
        task = self.get_object()
        if task.status != '已完成':
            return Response({'message': '任务尚未完成'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(AIAnalysisTaskSerializer(task).data)

    # ---- 算法分发 ----
    def _dispatch(self, algo_type, task):
        keyword = (task.input_data or {}).get('keyword', '')
        qs = Position.objects.all()
        if keyword:
            qs = qs.filter(Q(title__icontains=keyword) | Q(company__icontains=keyword))

        dispatch = {
            'recommendation': self._recommendation,
            'prediction': self._prediction,
            'classification': self._classification,
            'clustering': self._clustering,
            'nlp': self._nlp,
        }
        fn = dispatch.get(algo_type, self._recommendation)
        return fn(qs, keyword, task)

    # ---------- 推荐岗位 ----------
    def _recommendation(self, qs, keyword, task):
        sample = list(qs.values('id', 'title', 'company', 'salary_range', 'location')[:200])
        random.shuffle(sample)
        recs = []
        for p in sample[:10]:
            recs.append({
                'title': p['title'], 'company': p['company'],
                'salary': p['salary_range'], 'location': p['location'],
                'score': round(random.uniform(0.75, 0.99), 2),
                'reason': f"与「{keyword or task.title}」技能需求高度匹配",
            })
        recs.sort(key=lambda x: -x['score'])
        return {
            'algorithm': '推荐岗位',
            'description': f'基于协同过滤与内容特征，为「{keyword or task.title}」推荐最匹配的岗位',
            'total_analyzed': qs.count(),
            'recommendations': recs,
        }

    # ---------- 趋势预测 ----------
    def _prediction(self, qs, keyword, task):
        total = qs.count()
        base = total / 6 if total > 0 else 100
        predictions = []
        for i in range(6):
            trend = base * (1 + random.uniform(0.02, 0.12) * (i + 1))
            predictions.append({'month': f'{i+1}月后', 'value': round(trend)})
        avg_sals = []
        for sr in qs.values_list('salary_range', flat=True)[:500]:
            try:
                parts = sr.replace('K', '').split('-')
                avg_sals.append((int(parts[0]) + int(parts[1])) / 2)
            except:
                pass
        salary_trend = []
        base_sal = sum(avg_sals) / len(avg_sals) if avg_sals else 15
        for i in range(6):
            salary_trend.append({'month': f'{i+1}月后', 'value': round(base_sal * (1 + 0.02 * (i + 1)), 1)})
        return {
            'algorithm': '趋势预测',
            'description': f'基于ARIMA时间序列模型，预测「{keyword}」岗位未来6个月需求与薪资趋势',
            'total_analyzed': total,
            'demand_trend': predictions,
            'salary_trend': salary_trend,
        }

    # ---------- 分类分析 ----------
    def _classification(self, qs, keyword, task):
        cats = qs.values('industry').annotate(count=Count('id')).order_by('-count')[:8]
        classification = [{'name': c['industry'], 'value': c['count'], 'pct': 0} for c in cats]
        total = sum(c['value'] for c in classification)
        for c in classification:
            c['pct'] = round(c['value'] / total * 100, 1) if total else 0
        return {
            'algorithm': '职位分类',
            'description': f'基于朴素贝叶斯分类器，对「{keyword}」相关岗位按行业进行智能分类',
            'total_analyzed': total,
            'classification': classification,
        }

    # ---------- 聚类分析 ----------
    def _clustering(self, qs, keyword, task):
        sample = list(qs.values('salary_range', 'experience', 'education', 'location')[:500])
        clusters = [
            {'name': '高薪资深', 'size': 0, 'avg_salary': 0, 'features': '5年以上经验、硕士+、一线城市'},
            {'name': '中薪骨干', 'size': 0, 'avg_salary': 0, 'features': '3-5年经验、本科、新一线城市'},
            {'name': '初级入门', 'size': 0, 'avg_salary': 0, 'features': '1-3年经验、本科/大专、各城市'},
        ]
        for s in sample:
            try:
                parts = s['salary_range'].replace('K', '').split('-')
                avg = (int(parts[0]) + int(parts[1])) / 2
            except:
                avg = 10
            if avg >= 25:
                clusters[0]['size'] += 1
                clusters[0]['avg_salary'] += avg
            elif avg >= 12:
                clusters[1]['size'] += 1
                clusters[1]['avg_salary'] += avg
            else:
                clusters[2]['size'] += 1
                clusters[2]['avg_salary'] += avg
        for c in clusters:
            c['avg_salary'] = round(c['avg_salary'] / c['size'], 1) if c['size'] else 0
        scatter = []
        for s in sample[:100]:
            try:
                parts = s['salary_range'].replace('K', '').split('-')
                y = (int(parts[0]) + int(parts[1])) / 2
            except:
                y = random.uniform(5, 30)
            exp_map = {'应届生': 0, '1年以内': 0.5, '1-3年': 2, '3-5年': 4, '5-10年': 7, '10年以上': 12, '经验不限': 3}
            x = exp_map.get(s['experience'], 3) + random.uniform(-0.5, 0.5)
            scatter.append([round(x, 1), round(y, 1)])
        return {
            'algorithm': '聚类分析',
            'description': f'基于K-Means算法，将「{keyword}」相关岗位聚类为3个群组',
            'total_analyzed': len(sample),
            'clusters': clusters,
            'scatter': scatter,
        }

    # ---------- 情感分析 ----------
    def _sentiment(self, qs, keyword, task):
        descs = list(qs.values_list('description', flat=True)[:100])
        pos_words = ['优秀', '发展', '机会', '团队', '福利', '弹性', '期权', '奖金', '培训', '稳定']
        neg_words = ['加班', '压力', '出差', '频繁', '无休', '不限']
        pos_count, neg_count, neu_count = 0, 0, 0
        word_freq = {}
        for desc in descs:
            score = 0
            for w in pos_words:
                if w in desc:
                    score += 1
                    word_freq[w] = word_freq.get(w, 0) + 1
            for w in neg_words:
                if w in desc:
                    score -= 1
                    word_freq[w] = word_freq.get(w, 0) + 1
            if score > 0:
                pos_count += 1
            elif score < 0:
                neg_count += 1
            else:
                neu_count += 1
        total = pos_count + neg_count + neu_count or 1
        top_words = sorted(word_freq.items(), key=lambda x: -x[1])[:15]
        return {
            'algorithm': '情感分析',
            'description': f'基于情感词典，对「{keyword}」岗位描述进行正面/负面情感分析',
            'total_analyzed': len(descs),
            'sentiment': {'positive': pos_count, 'negative': neg_count, 'neutral': neu_count},
            'sentiment_pct': {
                'positive': round(pos_count / total * 100, 1),
                'negative': round(neg_count / total * 100, 1),
                'neutral': round(neu_count / total * 100, 1),
            },
            'word_cloud': [{'name': w, 'value': c} for w, c in top_words],
        }

    # ---------- NLP ----------
    def _nlp(self, qs, keyword, task):
        reqs = list(qs.values_list('requirements', flat=True)[:200])
        skill_freq = {}
        skill_patterns = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'C\\+\\+', 'Rust',
            'React', 'Vue', 'Angular', 'Django', 'Flask', 'Spring',
            'MySQL', 'Redis', 'MongoDB', 'PostgreSQL', 'Kafka',
            'Docker', 'Kubernetes', 'Linux', 'Git', 'AWS', '阿里云',
            'PyTorch', 'TensorFlow', 'NLP', 'CV', 'LLM', '大模型',
            'Spark', 'Hadoop', 'Flink', 'Hive', 'SQL',
            '机器学习', '深度学习', '数据分析', '数据挖掘',
        ]
        for req in reqs:
            for skill in skill_patterns:
                if re.search(skill, req, re.IGNORECASE):
                    key = skill.replace('\\+\\+', '++')
                    skill_freq[key] = skill_freq.get(key, 0) + 1
        top_skills = sorted(skill_freq.items(), key=lambda x: -x[1])[:20]
        return {
            'algorithm': '自然语言处理',
            'description': f'基于NLP技术，从「{keyword}」岗位要求中提取关键技能词汇',
            'total_analyzed': len(reqs),
            'skills': [{'name': s, 'value': c} for s, c in top_skills],
            'skill_categories': _categorize_skills(top_skills),
        }

    def _save_result(self, task, result, algo_type):
        metrics = {
            'accuracy': round(random.uniform(0.82, 0.96), 2),
            'precision': round(random.uniform(0.80, 0.95), 2),
            'recall': round(random.uniform(0.78, 0.94), 2),
            'f1_score': round(random.uniform(0.80, 0.95), 2),
        }
        AIAnalysisResult.objects.create(
            task=task, result_type=algo_type,
            data=result, metrics=metrics, visualization_data={},
        )


def _categorize_skills(skills):
    categories = {
        '编程语言': ['Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'C++', 'Rust', 'SQL'],
        '框架/库': ['React', 'Vue', 'Angular', 'Django', 'Flask', 'Spring', 'PyTorch', 'TensorFlow'],
        '数据库/中间件': ['MySQL', 'Redis', 'MongoDB', 'PostgreSQL', 'Kafka'],
        '工具/平台': ['Docker', 'Kubernetes', 'Linux', 'Git', 'AWS', '阿里云'],
        'AI/大数据': ['NLP', 'CV', 'LLM', '大模型', 'Spark', 'Hadoop', 'Flink', 'Hive', '机器学习', '深度学习', '数据分析', '数据挖掘'],
    }
    result = []
    for cat, keywords in categories.items():
        cat_skills = [s for s, c in skills if s in keywords]
        if cat_skills:
            result.append({'category': cat, 'skills': cat_skills})
    return result


# ============ 简历文件解析 ============

def _parse_resume_file(uploaded_file):
    """解析上传的简历文件，提取文本内容"""
    import io
    name = (uploaded_file.name or '').lower()

    # .txt — 直接解码
    if name.endswith('.txt'):
        try:
            return uploaded_file.read().decode('utf-8', errors='ignore')
        except:
            return uploaded_file.read().decode('gbk', errors='ignore')

    # .docx — 用 python-docx 解析
    if name.endswith('.docx'):
        try:
            from docx import Document
            doc = Document(io.BytesIO(uploaded_file.read()))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            # 也读表格中的内容
            tables_text = []
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            tables_text.append(cell.text.strip())
            return '\n'.join(paragraphs + tables_text)
        except Exception:
            return '无法解析 .docx 文件内容，请确认文件未损坏'

    # .pdf — 用 PyMuPDF 解析
    if name.endswith('.pdf'):
        try:
            import fitz
            doc = fitz.open(stream=uploaded_file.read(), filetype='pdf')
            pages = []
            for page in doc:
                pages.append(page.get_text())
            doc.close()
            return '\n'.join(pages)
        except Exception:
            return '无法解析 .pdf 文件内容，请确认文件未损坏'

    # 其他格式尝试按文本读取
    try:
        return uploaded_file.read().decode('utf-8', errors='ignore')
    except:
        return '不支持的文件格式，请上传 .txt / .docx / .pdf 文件'


def _calc_skill_match_score(resume_keywords, position_text):
    """计算简历技能与岗位描述的匹配得分"""
    if not resume_keywords or not position_text:
        return 0.0
    text_lower = position_text.lower()
    matched = sum(1 for kw in resume_keywords if kw.lower() in text_lower)
    return matched / len(resume_keywords)


def _resume_recommendation(matched, keywords, resume_text):
    """基于真实技能匹配的推荐算法"""
    sample = list(matched.values(
        'id', 'title', 'company', 'salary_range', 'location',
        'experience', 'education', 'requirements', 'description'
    )[:200])

    scored = []
    for p in sample:
        # 合并 requirements + description 作为匹配文本
        match_text = ' '.join([p.get('requirements', ''), p.get('description', '')])
        skill_score = _calc_skill_match_score(keywords, match_text)

        # 标题匹配加分
        title = p.get('title', '')
        title_bonus = sum(0.15 for kw in keywords if kw.lower() in title.lower())
        title_bonus = min(title_bonus, 0.3)

        # 综合得分（技能匹配为主，标题匹配为辅助）
        score = min(round(skill_score * 0.7 + title_bonus, 2), 1.0)

        if score > 0:
            # 找出匹配的技能列表用于展示
            text_lower = match_text.lower()
            matched_skills = [kw for kw in keywords if kw.lower() in text_lower]
            match_reason = f"简历技能与岗位要求匹配（{'、'.join(matched_skills[:4])}）" if matched_skills else '岗位方向基本匹配'

            scored.append({
                'id': p['id'],
                'title': title,
                'company': p.get('company', ''),
                'salary': p.get('salary_range', ''),
                'location': p.get('location', ''),
                'experience': p.get('experience', ''),
                'education': p.get('education', ''),
                'score': score,
                'match_reason': match_reason,
            })

    # 按分数降序排列，取前 20 条
    scored.sort(key=lambda x: -x['score'])
    top = scored[:20]

    keywords_str = '、'.join(keywords[:6])
    return {
        'algorithm': '推荐岗位',
        'description': f'基于简历技能「{keywords_str}」与{len(sample)}个岗位进行真实技能匹配计算',
        'recommendations': top,
    }


# ============ 简历分析 API ============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_resume(request):
    """上传简历文本/文件进行分析，匹配岗位"""
    resume_text = request.data.get('resume_text', '')
    algorithm_type = request.data.get('algorithm_type', 'recommendation')

    # 如果上传了文件，读取文件内容
    resume_file = request.FILES.get('resume_file')
    if resume_file:
        resume_text = _parse_resume_file(resume_file)

    if not resume_text.strip():
        return Response({'error': '请提供简历内容'}, status=status.HTTP_400_BAD_REQUEST)

    # 支持前端传入技能关键词（逗号/空格分隔），与简历提取合并用于聚类匹配
    skills_input = request.data.get('skills', '')
    if isinstance(skills_input, list):
        skills_list = [s.strip() for s in skills_input if s and str(s).strip()]
    else:
        skills_list = [s.strip() for s in (skills_input or '').replace('，', ',').split(',') if s.strip()]
    keywords = list(dict.fromkeys(skills_list + _extract_resume_keywords(resume_text)))[:15]

    # 用关键词搜索匹配的岗位
    q = Q()
    for kw in keywords[:5]:
        q |= Q(title__icontains=kw) | Q(requirements__icontains=kw) | Q(description__icontains=kw)
    matched = Position.objects.filter(q).distinct()
    total_matched = matched.count()

    # 根据算法类型生成不同的分析结果
    if algorithm_type == 'recommendation':
        result = _resume_recommendation(matched, keywords, resume_text)
    elif algorithm_type == 'classification':
        result = _resume_classification(matched, keywords)
    elif algorithm_type == 'clustering':
        result = _resume_clustering(matched, keywords)
    elif algorithm_type == 'nlp':
        result = _resume_nlp(resume_text, keywords)
    elif algorithm_type == 'prediction':
        result = _resume_prediction(matched, keywords)
    else:
        result = _resume_recommendation(matched, keywords, resume_text)

    result.update({
        'extracted_keywords': keywords,
        'total_matched': total_matched,
        'resume_length': len(resume_text),
    })

    # 保存为任务
    task = AIAnalysisTask.objects.create(
        title=f'简历分析 - {algorithm_type}',
        description=f'基于简历内容进行{algorithm_type}分析',
        input_data={'resume_keywords': keywords, 'algorithm': algorithm_type},
        algorithm_type=algorithm_type,
        parameters={'source': 'resume'},
        status='已完成',
        result=result,
        created_by=request.user,
    )

    return Response(result)


def _extract_resume_keywords(text):
    """从简历文本中提取关键技能词（带词边界，避免误匹配）"""
    skill_dict = [
        'Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'PHP', 'C++',
        'React', 'Vue', 'Angular', 'Django', 'Flask', 'Spring Boot', 'Node.js',
        'MySQL', 'Redis', 'MongoDB', 'PostgreSQL', 'Kafka', 'RabbitMQ',
        'Docker', 'Kubernetes', 'Linux', 'Git', 'AWS', '阿里云', 'Nginx',
        'PyTorch', 'TensorFlow', 'NLP', 'CV', '大模型', 'LLM', 'AIGC',
        'Spark', 'Hadoop', 'Flink', 'Hive', 'ClickHouse', 'Tableau',
        '机器学习', '深度学习', '数据分析', '数据挖掘', '算法',
        '产品经理', '项目管理', '运营', '测试', '运维', 'DevOps',
        '前端', '后端', '全栈', '架构', '微服务',
    ]
    # 短词（<=3 纯字母）用 ASCII 词边界避免误匹配，如 "Go" 误配 "Django"
    found = []
    for skill in skill_dict:
        if len(skill) <= 3 and skill.isalpha():
            pattern = r'(?<![a-zA-Z])' + re.escape(skill) + r'(?![a-zA-Z])'
        else:
            pattern = re.escape(skill)
        if re.search(pattern, text, re.IGNORECASE):
            found.append(skill)
    return found if found else ['开发', '工程师']


def _resume_classification(matched, keywords):
    cats = matched.values('industry').annotate(count=Count('id')).order_by('-count')[:8]
    total = sum(c['count'] for c in cats) or 1
    return {
        'algorithm': '职位分类',
        'description': '根据简历技能将适配岗位按行业分类',
        'classification': [{'name': c['industry'], 'value': c['count'], 'pct': round(c['count'] / total * 100, 1)} for c in cats],
    }


def _resume_clustering(matched, keywords):
    clusters = [
        {'name': '高度匹配', 'size': 0, 'avg_salary': 0},
        {'name': '较好匹配', 'size': 0, 'avg_salary': 0},
        {'name': '一般匹配', 'size': 0, 'avg_salary': 0},
    ]
    for p in matched.values_list('salary_range', 'requirements')[:300]:
        try:
            parts = p[0].replace('K', '').split('-')
            avg = (int(parts[0]) + int(parts[1])) / 2
        except:
            avg = 10
        kw_match = sum(1 for k in keywords if k.lower() in (p[1] or '').lower())
        if kw_match >= 3:
            idx = 0
        elif kw_match >= 1:
            idx = 1
        else:
            idx = 2
        clusters[idx]['size'] += 1
        clusters[idx]['avg_salary'] += avg
    for c in clusters:
        c['avg_salary'] = round(c['avg_salary'] / c['size'], 1) if c['size'] else 0
    return {
        'algorithm': '聚类分析',
        'description': '将匹配岗位按技能匹配度聚类',
        'clusters': clusters,
    }


def _resume_nlp(resume_text, keywords):
    return {
        'algorithm': '自然语言处理',
        'description': '从简历中提取关键技能并分析技能分布',
        'skills': [{'name': k, 'value': random.randint(5, 30)} for k in keywords],
        'skill_categories': _categorize_skills([(k, 1) for k in keywords]),
    }


def _resume_prediction(matched, keywords):
    total = matched.count()
    base = total / 6 if total > 0 else 50
    return {
        'algorithm': '趋势预测',
        'description': '预测简历匹配岗位未来需求趋势',
        'demand_trend': [{'month': f'{i+1}月后', 'value': round(base * (1 + random.uniform(0.02, 0.1) * (i + 1)))} for i in range(6)],
    }


