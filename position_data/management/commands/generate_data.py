"""
生成 15000 条真实感岗位数据的管理命令
用法: python manage.py generate_data
"""
import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from position_data.models import Position
from statistics_app.models import IndustryStatistics, SalaryStatistics

# ============================================================
#  基础数据词典 —— 尽量贴近 BOSS 直聘真实岗位
# ============================================================

CITIES = {
    '北京': 2200, '上海': 2000, '深圳': 1600, '广州': 1200,
    '杭州': 1000, '成都': 800, '武汉': 700, '南京': 700,
    '西安': 600, '苏州': 500, '长沙': 400, '重庆': 400,
    '郑州': 350, '天津': 350, '青岛': 300, '合肥': 300,
    '厦门': 250, '大连': 200, '宁波': 200, '东莞': 200,
    '佛山': 150, '无锡': 150, '珠海': 150, '福州': 150,
    '济南': 150, '昆明': 100, '贵阳': 100, '银川': 50,
}

INDUSTRIES = {
    '互联网/IT': 4000, '金融': 1500, '教育培训': 1200,
    '电子商务': 1000, '医疗健康': 800, '房地产/建筑': 700,
    '制造业': 600, '物流/供应链': 500, '文化传媒': 400,
    '汽车': 350, '能源/环保': 300, '零售/消费': 300,
    '通信/电子': 500, '游戏': 350, '人工智能': 500,
    '农业/食品': 200, '旅游/酒店': 200, '法律/咨询': 200,
    '政府/公共事业': 150, '其他': 250,
}

COMPANIES_BY_INDUSTRY = {
    '互联网/IT': [
        ('字节跳动', '已上市·10000人以上'), ('腾讯', '已上市·10000人以上'), ('阿里巴巴', '已上市·10000人以上'),
        ('美团', '已上市·10000人以上'), ('百度', '已上市·10000人以上'), ('京东', '已上市·10000人以上'),
        ('网易', '已上市·10000人以上'), ('小米', '已上市·10000人以上'), ('华为', '未上市·10000人以上'),
        ('滴滴出行', 'D轮·10000人以上'), ('快手', '已上市·10000人以上'), ('拼多多', '已上市·10000人以上'),
        ('哔哩哔哩', '已上市·5000-10000人'), ('携程', '已上市·10000人以上'), ('58同城', '已上市·5000-10000人'),
        ('新浪微博', '已上市·1000-5000人'), ('知乎', '已上市·1000-5000人'), ('OPPO', '未上市·10000人以上'),
        ('vivo', '未上市·10000人以上'), ('中兴通讯', '已上市·10000人以上'), ('浪潮集团', '已上市·10000人以上'),
        ('紫光集团', '已上市·5000-10000人'), ('用友网络', '已上市·10000人以上'), ('科大讯飞', '已上市·10000人以上'),
        ('深信服', '已上市·5000-10000人'), ('奇安信', '已上市·5000-10000人'), ('启明星辰', '已上市·1000-5000人'),
        ('蚂蚁集团', '未上市·10000人以上'), ('商汤科技', '已上市·1000-5000人'), ('旷视科技', 'D轮·1000-5000人'),
        ('图森未来', '已上市·500-1000人'), ('思科中国', '已上市·1000-5000人'), ('甲骨文中国', '已上市·1000-5000人'),
        ('微软中国', '已上市·1000-5000人'), ('谷歌中国', '已上市·500-1000人'), ('IBM中国', '已上市·1000-5000人'),
        ('博瑞信息', 'B轮·100-500人'), ('云智慧科技', 'C轮·500-1000人'), ('数美科技', 'D轮·500-1000人'),
        ('每日优鲜', '已上市·1000-5000人'), ('达达集团', '已上市·1000-5000人'), ('货拉拉', 'E轮·5000-10000人'),
    ],
    '金融': [
        ('中国银行', '已上市·10000人以上'), ('工商银行', '已上市·10000人以上'), ('建设银行', '已上市·10000人以上'),
        ('招商银行', '已上市·10000人以上'), ('平安集团', '已上市·10000人以上'), ('中信证券', '已上市·10000人以上'),
        ('蚂蚁金服', '未上市·10000人以上'), ('陆金所', '已上市·5000-10000人'), ('微众银行', '未上市·5000-10000人'),
        ('京东数科', '未上市·5000-10000人'), ('度小满金融', '未上市·1000-5000人'), ('马上消费金融', '未上市·1000-5000人'),
        ('中泰证券', '已上市·5000-10000人'), ('国泰君安', '已上市·10000人以上'), ('广发证券', '已上市·10000人以上'),
    ],
    '教育培训': [
        ('好未来', '已上市·10000人以上'), ('新东方', '已上市·10000人以上'), ('猿辅导', 'E轮·10000人以上'),
        ('作业帮', 'E轮·10000人以上'), ('得到', 'C轮·1000-5000人'), ('网易有道', '已上市·5000-10000人'),
        ('高途集团', '已上市·5000-10000人'), ('掌门教育', 'E轮·5000-10000人'), ('松鼠AI', 'C轮·500-1000人'),
        ('粉笔教育', '已上市·5000-10000人'), ('中公教育', '已上市·10000人以上'), ('华图教育', '未上市·10000人以上'),
    ],
    '电子商务': [
        ('淘宝', '已上市·10000人以上'), ('天猫', '已上市·10000人以上'), ('京东商城', '已上市·10000人以上'),
        ('拼多多', '已上市·10000人以上'), ('唯品会', '已上市·5000-10000人'), ('苏宁易购', '已上市·10000人以上'),
        ('网易严选', '已上市·1000-5000人'), ('小红书', 'E轮·5000-10000人'), ('蘑菇街', '已上市·500-1000人'),
        ('得物(毒)', 'D轮·1000-5000人'), ('有赞', '已上市·1000-5000人'), ('微盟', '已上市·1000-5000人'),
    ],
    '医疗健康': [
        ('平安好医生', '已上市·5000-10000人'), ('丁香园', 'E轮·1000-5000人'), ('微医', 'E轮·1000-5000人'),
        ('药明康德', '已上市·10000人以上'), ('迈瑞医疗', '已上市·10000人以上'), ('联影医疗', '已上市·5000-10000人'),
        ('春雨医生', 'D轮·500-1000人'), ('好大夫在线', 'D轮·500-1000人'), ('京东健康', '已上市·5000-10000人'),
        ('阿里健康', '已上市·1000-5000人'),
    ],
    '房地产/建筑': [
        ('万科', '已上市·10000人以上'), ('碧桂园', '已上市·10000人以上'), ('中海地产', '已上市·10000人以上'),
        ('保利发展', '已上市·10000人以上'), ('龙湖集团', '已上市·10000人以上'), ('融创中国', '已上市·10000人以上'),
        ('绿城中国', '已上市·5000-10000人'), ('中建集团', '未上市·10000人以上'), ('中铁建设', '已上市·10000人以上'),
    ],
    '制造业': [
        ('比亚迪', '已上市·10000人以上'), ('格力电器', '已上市·10000人以上'), ('美的集团', '已上市·10000人以上'),
        ('海尔智家', '已上市·10000人以上'), ('富士康', '未上市·10000人以上'), ('三一重工', '已上市·10000人以上'),
        ('宁德时代', '已上市·10000人以上'), ('立讯精密', '已上市·10000人以上'), ('中芯国际', '已上市·10000人以上'),
    ],
    '物流/供应链': [
        ('顺丰速运', '已上市·10000人以上'), ('京东物流', '已上市·10000人以上'), ('中通快递', '已上市·10000人以上'),
        ('圆通速递', '已上市·10000人以上'), ('韵达快递', '已上市·10000人以上'), ('菜鸟网络', '未上市·10000人以上'),
        ('德邦快递', '已上市·10000人以上'), ('极兔速递', 'D轮·10000人以上'),
    ],
    '文化传媒': [
        ('字节跳动(抖音)', '已上市·10000人以上'), ('快手科技', '已上市·10000人以上'), ('爱奇艺', '已上市·5000-10000人'),
        ('优酷', '已上市·5000-10000人'), ('芒果TV', '已上市·1000-5000人'), ('喜马拉雅', 'E轮·1000-5000人'),
        ('虎牙直播', '已上市·1000-5000人'), ('斗鱼', '已上市·1000-5000人'),
    ],
    '汽车': [
        ('蔚来汽车', '已上市·10000人以上'), ('理想汽车', '已上市·10000人以上'), ('小鹏汽车', '已上市·10000人以上'),
        ('比亚迪汽车', '已上市·10000人以上'), ('吉利汽车', '已上市·10000人以上'), ('长城汽车', '已上市·10000人以上'),
        ('特斯拉中国', '已上市·5000-10000人'), ('上汽集团', '已上市·10000人以上'), ('广汽集团', '已上市·10000人以上'),
    ],
    '能源/环保': [
        ('宁德时代', '已上市·10000人以上'), ('隆基绿能', '已上市·10000人以上'), ('阳光电源', '已上市·5000-10000人'),
        ('金风科技', '已上市·5000-10000人'), ('通威股份', '已上市·10000人以上'), ('中国石油', '已上市·10000人以上'),
        ('中国石化', '已上市·10000人以上'),
    ],
    '零售/消费': [
        ('瑞幸咖啡', '已上市·10000人以上'), ('喜茶', 'C轮·5000-10000人'), ('奈雪的茶', '已上市·5000-10000人'),
        ('名创优品', '已上市·10000人以上'), ('永辉超市', '已上市·10000人以上'), ('盒马鲜生', '未上市·10000人以上'),
        ('元气森林', 'C轮·1000-5000人'), ('泡泡玛特', '已上市·1000-5000人'),
    ],
    '通信/电子': [
        ('华为', '未上市·10000人以上'), ('中兴通讯', '已上市·10000人以上'), ('大疆创新', '未上市·10000人以上'),
        ('海康威视', '已上市·10000人以上'), ('紫光展锐', '未上市·5000-10000人'), ('联发科中国', '已上市·5000-10000人'),
        ('中国移动', '已上市·10000人以上'), ('中国电信', '已上市·10000人以上'), ('中国联通', '已上市·10000人以上'),
    ],
    '游戏': [
        ('腾讯游戏', '已上市·10000人以上'), ('网易游戏', '已上市·10000人以上'), ('米哈游', '未上市·5000-10000人'),
        ('莉莉丝游戏', '未上市·1000-5000人'), ('叠纸游戏', '未上市·500-1000人'), ('鹰角网络', '未上市·500-1000人'),
        ('心动网络', '已上市·1000-5000人'), ('西山居', '未上市·1000-5000人'), ('完美世界', '已上市·5000-10000人'),
    ],
    '人工智能': [
        ('商汤科技', '已上市·1000-5000人'), ('旷视科技', 'D轮·1000-5000人'), ('科大讯飞', '已上市·10000人以上'),
        ('云从科技', '已上市·1000-5000人'), ('依图科技', 'D轮·500-1000人'), ('第四范式', 'D轮·1000-5000人'),
        ('地平线', 'C轮·1000-5000人'), ('寒武纪', '已上市·1000-5000人'), ('百川智能', 'A轮·100-500人'),
        ('月之暗面', 'B轮·100-500人'), ('智谱AI', 'B轮·500-1000人'), ('MiniMax', 'B轮·500-1000人'),
    ],
}

# 为没有单独列出的行业提供通用公司
DEFAULT_COMPANIES = [
    ('万达集团', '未上市·10000人以上'), ('海尔集团', '已上市·10000人以上'),
    ('联想集团', '已上市·10000人以上'), ('TCL科技', '已上市·10000人以上'),
    ('中粮集团', '未上市·10000人以上'), ('伊利集团', '已上市·10000人以上'),
    ('蒙牛乳业', '已上市·10000人以上'), ('海底捞', '已上市·10000人以上'),
    ('星巴克中国', '已上市·10000人以上'), ('麦当劳中国', '已上市·10000人以上'),
    ('万豪酒店', '已上市·10000人以上'), ('希尔顿酒店', '已上市·10000人以上'),
]

JOBS_BY_INDUSTRY = {
    '互联网/IT': [
        'Python开发工程师', 'Java开发工程师', '前端开发工程师', '后端开发工程师', '全栈开发工程师',
        '高级Java开发', '资深前端工程师', 'Go语言开发', 'C++开发工程师', 'PHP开发工程师',
        'iOS开发工程师', 'Android开发工程师', 'Flutter开发工程师', 'React Native开发',
        '测试工程师', '测试开发工程师', '自动化测试工程师', '性能测试工程师',
        '运维工程师', 'DevOps工程师', 'SRE工程师', '云计算工程师',
        '项目经理', '产品经理', '高级产品经理', '产品总监',
        'UI设计师', 'UX设计师', '交互设计师', '视觉设计师',
        '数据分析师', '数据开发工程师', '大数据工程师', 'ETL工程师',
        '架构师', '技术总监', 'CTO', '技术经理', '研发主管',
        'DBA', 'MySQL DBA', '网络工程师', '安全工程师', '渗透测试工程师',
    ],
    '金融': [
        '风控工程师', '量化开发工程师', '金融产品经理', '投资经理', '基金经理',
        '风险分析师', '信贷审核员', '银行客户经理', '理财顾问', '合规专员',
        '精算师', '保险产品经理', '金融数据分析师', '反欺诈工程师', '支付产品经理',
    ],
    '教育培训': [
        '教研经理', '课程设计师', '在线教育产品经理', '辅导老师', '学科教师',
        'AI教育产品经理', '教育运营', '教务管理', '内容编辑', '培训讲师',
    ],
    '电子商务': [
        '电商运营', '直播运营', '商品运营', '用户运营', '活动运营',
        '供应链经理', '采购经理', '仓储管理', '电商产品经理', '新媒体运营',
        '社群运营', '内容运营', '短视频运营', 'SEO优化师', 'SEM专员',
    ],
    '医疗健康': [
        '医疗数据分析师', '医药代表', '临床研究员', '药品研发', '医疗产品经理',
        '医学编辑', '健康管理师', '医疗AI工程师', '生物信息工程师', '注册专员',
    ],
    '房地产/建筑': [
        '建筑设计师', '土木工程师', '项目经理', '施工员', '预算员',
        '置业顾问', '房产经纪人', 'BIM工程师', '造价工程师', '监理工程师',
    ],
    '制造业': [
        '机械工程师', '电气工程师', '工艺工程师', '质量工程师', 'IE工程师',
        '自动化工程师', '生产经理', '采购工程师', '供应链专员', '仓库管理',
    ],
    '物流/供应链': [
        '物流经理', '仓储主管', '调度员', '供应链分析师', '采购专员',
        '运输经理', '报关员', '货运代理', '物流方案设计', '配送主管',
    ],
    '文化传媒': [
        '视频编辑', '内容策划', '新媒体编辑', '文案策划', '直播策划',
        '编导', '短视频导演', '摄影师', '平面设计师', '品牌经理',
    ],
    '汽车': [
        '自动驾驶算法工程师', '车辆工程师', '嵌入式开发工程师', '电池工程师', '电机工程师',
        '智能座舱开发', '车联网工程师', 'ADAS工程师', '整车测试工程师', '汽车销售顾问',
    ],
    '能源/环保': [
        '电力工程师', '新能源研发', '光伏工程师', '储能工程师', '环保工程师',
        '碳交易分析师', '风电工程师', '能源管理', '电站运维', '安全环保专员',
    ],
    '零售/消费': [
        '门店经理', '区域经理', '品类经理', '买手', '市场推广',
        '会员运营', '客户服务经理', '视觉陈列师', '招商经理', '零售培训师',
    ],
    '通信/电子': [
        '通信工程师', '射频工程师', '硬件工程师', 'FPGA工程师', '嵌入式工程师',
        '光通信工程师', '无线网络工程师', '芯片设计工程师', 'IC验证工程师', 'PCB工程师',
    ],
    '游戏': [
        '游戏策划', '游戏开发工程师', '游戏美术', 'Unity开发工程师', 'UE4开发工程师',
        '游戏运营', '游戏测试', '关卡设计师', '游戏特效设计', '技术美术',
    ],
    '人工智能': [
        'AI算法工程师', '机器学习工程师', '深度学习工程师', 'NLP工程师', 'CV算法工程师',
        '推荐系统工程师', '语音算法工程师', '大模型开发工程师', 'AI产品经理', 'AI训练师',
        '数据标注主管', 'MLOps工程师', '知识图谱工程师', 'AIGC工程师', 'Prompt工程师',
    ],
}

DEFAULT_JOBS = [
    '项目经理', '产品经理', '运营经理', '市场经理', '人事经理',
    '行政主管', '财务会计', '法务专员', '商务经理', '客服专员',
    '数据分析师', '软件开发工程师', '销售经理', '总经理助理', '品牌经理',
]

EDUCATION_WEIGHTS = [('大专', 15), ('本科', 55), ('硕士', 20), ('博士', 5), ('学历不限', 5)]
EXPERIENCE_WEIGHTS = [
    ('应届生', 8), ('1年以内', 10), ('1-3年', 30), ('3-5年', 25),
    ('5-10年', 18), ('10年以上', 4), ('经验不限', 5),
]
POSITION_TYPE_WEIGHTS = [('全职', 85), ('兼职', 5), ('实习', 8), ('合同', 2)]

# 薪资与经验 / 学历关联
SALARY_RANGES = {
    '应届生':   [(3, 5), (4, 6), (5, 8), (6, 10)],
    '1年以内':  [(4, 6), (5, 8), (6, 10), (8, 12)],
    '1-3年':    [(6, 10), (8, 13), (10, 15), (12, 18), (10, 20)],
    '3-5年':    [(10, 15), (12, 20), (15, 25), (18, 30), (20, 35)],
    '5-10年':   [(15, 25), (20, 35), (25, 40), (30, 50), (25, 45)],
    '10年以上': [(25, 40), (30, 50), (35, 60), (40, 70), (50, 80)],
    '经验不限': [(5, 8), (6, 10), (8, 15), (10, 20), (15, 25)],
}

# AI / 互联网 薪资上浮系数
HIGH_SALARY_INDUSTRIES = {'互联网/IT': 1.3, '人工智能': 1.5, '金融': 1.3, '游戏': 1.2}

BENEFITS_POOL = [
    '五险一金', '带薪年假', '年终奖金', '股票期权', '弹性工作',
    '定期体检', '免费三餐', '补充医疗保险', '员工旅游', '节日福利',
    '租房补贴', '交通补贴', '通讯补贴', '加班补贴', '学习基金',
    '健身房', '下午茶', '团建活动', '六险一金', '带薪病假',
]

SKILLS_MAP = {
    'Python': ['Python', 'Django', 'Flask', 'FastAPI', 'pandas', 'numpy'],
    'Java': ['Java', 'Spring Boot', 'MyBatis', 'Redis', 'Kafka', 'MySQL'],
    '前端': ['JavaScript', 'TypeScript', 'React', 'Vue.js', 'HTML/CSS', 'Webpack'],
    '后端': ['Golang', 'Rust', 'Node.js', 'PostgreSQL', 'MongoDB', 'Docker'],
    '测试': ['Selenium', 'JMeter', 'Postman', 'Jenkins', 'CI/CD', 'Linux'],
    '数据': ['SQL', 'Spark', 'Hive', 'Flink', 'Hadoop', 'ClickHouse', 'Tableau'],
    'AI': ['PyTorch', 'TensorFlow', 'HuggingFace', 'LLM', 'NLP', 'OpenCV', 'CUDA'],
    '运维': ['Linux', 'Docker', 'Kubernetes', 'Ansible', 'Prometheus', 'AWS', '阿里云'],
    '产品': ['Axure', 'Figma', 'Sketch', '用户调研', '数据分析', '竞品分析', 'PRD撰写'],
    '设计': ['Figma', 'Sketch', 'Photoshop', 'Illustrator', 'After Effects'],
    '通用': ['Office', '沟通协调', '团队协作', '项目管理', '文档撰写'],
}


def weighted_choice(items_weights):
    items, weights = zip(*items_weights)
    return random.choices(items, weights=weights, k=1)[0]


def get_skills_for_job(title):
    title_lower = title.lower()
    matched = []
    if 'python' in title_lower:
        matched = SKILLS_MAP['Python']
    elif 'java' in title_lower and 'javascript' not in title_lower:
        matched = SKILLS_MAP['Java']
    elif '前端' in title_lower or 'react' in title_lower or 'vue' in title_lower or 'flutter' in title_lower:
        matched = SKILLS_MAP['前端']
    elif '后端' in title_lower or '全栈' in title_lower or 'go' in title_lower:
        matched = SKILLS_MAP['后端']
    elif '测试' in title_lower:
        matched = SKILLS_MAP['测试']
    elif '数据' in title_lower or 'etl' in title_lower or 'dba' in title_lower:
        matched = SKILLS_MAP['数据']
    elif 'ai' in title_lower or '算法' in title_lower or '机器学习' in title_lower or '深度学习' in title_lower or 'nlp' in title_lower or '大模型' in title_lower:
        matched = SKILLS_MAP['AI']
    elif '运维' in title_lower or 'devops' in title_lower or 'sre' in title_lower:
        matched = SKILLS_MAP['运维']
    elif '产品' in title_lower:
        matched = SKILLS_MAP['产品']
    elif '设计' in title_lower or 'ui' in title_lower or 'ux' in title_lower:
        matched = SKILLS_MAP['设计']
    else:
        matched = SKILLS_MAP['通用']
    return random.sample(matched, min(random.randint(3, 5), len(matched)))


def generate_description(title, company, skills):
    intros = [
        f"我们正在寻找一位优秀的{title}加入{company}团队。",
        f"{company}诚聘{title}，期待你的加入！",
        f"作为{title}，你将参与公司核心业务的研发与迭代。",
    ]
    duties = [
        f"负责公司核心业务系统的设计、开发和维护",
        f"参与系统架构设计，推动技术选型和方案落地",
        f"与产品、设计团队紧密合作，确保项目高质量交付",
        f"持续优化系统性能，提升用户体验",
        f"参与代码评审，保证代码质量和规范性",
        f"编写技术文档，分享技术经验",
        f"跟进业界前沿技术，推动技术升级迭代",
    ]
    return random.choice(intros) + '\n\n岗位职责：\n' + '\n'.join(f'{i+1}. {d}' for i, d in enumerate(random.sample(duties, min(5, len(duties)))))


def generate_requirements(education, experience, skills):
    base = [
        f"{education}及以上学历，计算机相关专业优先",
        f"{experience}相关工作经验",
    ]
    skill_reqs = [f"熟悉{s}，有实际项目经验" for s in skills[:3]]
    general = [
        "良好的沟通能力和团队协作精神",
        "有较强的学习能力和自驱力",
        "有大型项目经验者优先",
    ]
    all_reqs = base + skill_reqs + random.sample(general, 2)
    return '\n'.join(f'{i+1}. {r}' for i, r in enumerate(all_reqs))


class Command(BaseCommand):
    help = '生成 15000 条真实感岗位数据并填充统计表'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=15000, help='生成数量')
        parser.add_argument('--clear', action='store_true', help='先清空已有数据')

    def handle(self, *args, **options):
        count = options['count']
        if options['clear']:
            self.stdout.write('清空现有数据...')
            Position.objects.all().delete()
            IndustryStatistics.objects.all().delete()
            SalaryStatistics.objects.all().delete()

        self.stdout.write(f'开始生成 {count} 条岗位数据...')

        # 按行业权重分配数量
        total_weight = sum(INDUSTRIES.values())
        industry_counts = {}
        remaining = count
        industry_list = list(INDUSTRIES.items())
        for i, (industry, weight) in enumerate(industry_list):
            if i == len(industry_list) - 1:
                industry_counts[industry] = remaining
            else:
                n = round(count * weight / total_weight)
                industry_counts[industry] = n
                remaining -= n

        positions = []
        today = date.today()
        batch_num = 0

        for industry, num in industry_counts.items():
            companies = COMPANIES_BY_INDUSTRY.get(industry, DEFAULT_COMPANIES)
            jobs = JOBS_BY_INDUSTRY.get(industry, DEFAULT_JOBS)
            salary_factor = HIGH_SALARY_INDUSTRIES.get(industry, 1.0)

            # 按城市权重分配本行业数量
            city_list = list(CITIES.items())
            city_total_w = sum(CITIES.values())

            for _ in range(num):
                city = weighted_choice([(c, w) for c, w in city_list])
                title = random.choice(jobs)
                company_name, company_tag = random.choice(companies)
                education = weighted_choice(EDUCATION_WEIGHTS)
                experience = weighted_choice(EXPERIENCE_WEIGHTS)
                position_type = weighted_choice(POSITION_TYPE_WEIGHTS)

                # 薪资
                sal_ranges = SALARY_RANGES.get(experience, [(8, 15)])
                low, high = random.choice(sal_ranges)
                low = int(low * salary_factor)
                high = int(high * salary_factor)
                # 城市系数
                if city in ('北京', '上海', '深圳'):
                    low = int(low * 1.15)
                    high = int(high * 1.15)
                elif city in ('杭州', '广州', '南京', '苏州'):
                    low = int(low * 1.05)
                    high = int(high * 1.05)
                salary_range = f'{low}-{high}K'

                skills = get_skills_for_job(title)
                description = generate_description(title, company_name, skills)
                requirements = generate_requirements(education, experience, skills)
                benefits = '、'.join(random.sample(BENEFITS_POOL, random.randint(4, 8)))
                published_date = today - timedelta(days=random.randint(0, 90))

                positions.append(Position(
                    title=title,
                    company=company_name,
                    location=city,
                    salary_range=salary_range,
                    position_type=position_type,
                    requirements=requirements,
                    description=description,
                    benefits=benefits,
                    education=education,
                    experience=experience,
                    industry=industry,
                    source_url=f'https://www.zhipin.com/job_detail/{random.randint(100000, 999999)}.html',
                    published_date=published_date,
                ))

                # 每 2000 条批量写入一次
                if len(positions) >= 2000:
                    batch_num += 1
                    Position.objects.bulk_create(positions, ignore_conflicts=True)
                    self.stdout.write(f'  已写入 {batch_num * 2000} 条...')
                    positions = []

        # 写入剩余
        if positions:
            Position.objects.bulk_create(positions, ignore_conflicts=True)

        total = Position.objects.count()
        self.stdout.write(self.style.SUCCESS(f'✅ 岗位数据生成完毕，共 {total} 条'))

        # ============ 生成行业统计 ============
        self.stdout.write('生成行业统计数据...')
        for industry in INDUSTRIES:
            industry_positions = Position.objects.filter(industry=industry)
            cnt = industry_positions.count()
            if cnt == 0:
                continue

            # 计算平均薪资
            salaries = []
            for p in industry_positions.values_list('salary_range', flat=True)[:500]:
                try:
                    parts = p.replace('K', '').split('-')
                    salaries.append((int(parts[0]) + int(parts[1])) / 2)
                except:
                    pass
            avg_sal = sum(salaries) / len(salaries) if salaries else 15

            companies = list(industry_positions.values_list('company', flat=True).distinct()[:10])
            skills_pool = JOBS_BY_INDUSTRY.get(industry, DEFAULT_JOBS)

            IndustryStatistics.objects.update_or_create(
                industry=industry,
                defaults={
                    'total_positions': cnt,
                    'avg_salary': Decimal(str(round(avg_sal, 2))),
                    'top_companies': companies,
                    'hot_skills': skills_pool[:8],
                    'growth_rate': Decimal(str(round(random.uniform(2.0, 25.0), 2))),
                }
            )
        self.stdout.write(self.style.SUCCESS('✅ 行业统计数据完毕'))

        # ============ 生成薪资统计 ============
        self.stdout.write('生成薪资统计数据...')
        top_titles = Position.objects.values_list('title', flat=True).distinct()[:50]
        top_cities = list(CITIES.keys())[:10]

        for title in top_titles:
            for city in top_cities:
                qs = Position.objects.filter(title=title, location=city)
                cnt = qs.count()
                if cnt < 3:
                    continue
                salaries = []
                for p in qs.values_list('salary_range', flat=True):
                    try:
                        parts = p.replace('K', '').split('-')
                        salaries.append((int(parts[0]) + int(parts[1])) / 2)
                    except:
                        pass
                if not salaries:
                    continue

                salaries.sort()
                avg = sum(salaries) / len(salaries)
                median = salaries[len(salaries) // 2]

                SalaryStatistics.objects.update_or_create(
                    position_title=title, location=city,
                    defaults={
                        'min_salary': Decimal(str(round(min(salaries), 2))),
                        'max_salary': Decimal(str(round(max(salaries), 2))),
                        'avg_salary': Decimal(str(round(avg, 2))),
                        'median_salary': Decimal(str(round(median, 2))),
                        'sample_size': cnt,
                    }
                )
        self.stdout.write(self.style.SUCCESS('✅ 薪资统计数据完毕'))
        self.stdout.write(self.style.SUCCESS(f'\n🎉 全部完成！共生成 {total} 条岗位 + 行业统计 + 薪资统计'))
