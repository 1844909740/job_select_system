"""
招聘网站职位数据爬虫
从智联招聘(zhaopin.com)爬取职位信息，解析后存入数据库
"""
import re
import time
import random
import json
import logging
from datetime import date, datetime
from urllib.parse import urlencode
from typing import List, Dict, Optional

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

try:
    import cloudscraper
except ImportError:
    cloudscraper = None

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def _parse_salary_zh(salary_str: str) -> Optional[str]:
    """将中文薪资格式转为统一的 K 月薪格式

    输入: "9000-12000元" / "5000-10000" / "25000以上"
    输出: "9-12K" / "5-10K" / "25K+"
    """
    if not salary_str:
        return None
    salary_str = salary_str.replace("元", "").replace("¥", "").strip()

    # 范围格式: 9000-12000
    m = re.search(r'(\d+)\s*[-–to]+\s*(\d+)', salary_str)
    if m:
        low = int(m.group(1))
        high = int(m.group(2))
        # 如果数值很大（可能是年薪），除以12
        if low > 100000:
            low_k = low // 12 // 1000
            high_k = high // 12 // 1000
        elif low > 1000:
            low_k = low // 1000
            high_k = high // 1000
        else:
            low_k = low
            high_k = high
        return f"{low_k}-{high_k}K"

    # 以上格式: 25000以上 / 20000+
    m = re.search(r'(\d+)\s*(?:以上|K?\s*\+)', salary_str)
    if m:
        val = int(m.group(1))
        return f"{val // 1000}K+"

    return None


def _infer_industry(title: str) -> str:
    """从职位名称推断所属行业"""
    t = title.lower()
    if any(w in t for w in ["python", "java", "前端", "后端", "全栈", "developer",
                             "engineer", "software", "full-stack", "full stack",
                             "back-end", "backend", "front-end", "frontend",
                             "go", "rust", "react", "vue", "node", "程序员", "devops",
                             "sre", "infrastructure", "platform engineer",
                             "测试", "测试开发", "qa", "运维", "embedded",
                             "c++", "golang", "rust"]):
        return "互联网/IT"
    if any(w in t for w in ["machine learning", "deep learning", "nlp", "ai",
                             "artificial intelligence", "llm", "data scientist",
                             "算法", "数据", "推荐系统"]):
        return "人工智能"
    if any(w in t for w in ["product manager", "product designer", "产品经理"]):
        return "互联网/IT"
    if any(w in t for w in ["销售", "市场", "营销", "商务", "sales", "marketing"]):
        return "零售/消费"
    if any(w in t for w in ["运营", "新媒体", "内容", "社群", "content"]):
        return "文化传媒"
    if any(w in t for w in ["designer", "ui", "ux", "visual", "graphic", "设计"]):
        return "互联网/IT"
    if any(w in t for w in ["finance", "financial", "investment", "金融", "风控"]):
        return "金融"
    if any(w in t for w in ["teacher", "education", "instructor", "trainer", "教师"]):
        return "教育培训"
    if any(w in t for w in ["accountant", "hr", "human resources", "legal",
                             "人事", "行政", "文员", "助理", "后勤"]):
        return "其他"
    if any(w in t for w in ["司机", "保安", "保洁", "厨师", "配送", "骑手",
                             "普工", "操作工", "服务员", "收银"]):
        return "服务业"
    if any(w in t for w in ["医生", "护士", "医药", "医疗", "临床", "护理"]):
        return "医疗健康"
    return "互联网/IT"


class ZhaopinScraper:
    """智联招聘爬虫"""

    BASE_URL = "https://s.zhaopin.com"
    SEARCH_KEYWORDS = [
        "Python", "Java", "前端", "后端", "全栈",
        "算法", "数据分析", "机器学习",
        "产品经理", "测试", "运维",
        "C++", "Golang", "嵌入式",
    ]
    # 全国城市代码
    CITY_CODE = "全国"

    def __init__(self):
        if cloudscraper is None:
            raise ImportError("cloudscraper is required. Install with: pip install cloudscraper")
        self.session = cloudscraper.create_scraper()
        self.session.headers.update(REQUEST_HEADERS)

    @staticmethod
    def _is_relevant(title: str) -> bool:
        """排除明显不相关的蓝领岗位，保留白领及以上职位"""
        t = title.lower()
        # 排除明显不相关的蓝领/体力劳动岗位
        exclude = [
            "洗碗", "骑手", "配送", "配送员", "保安", "保洁", "厨师",
            "普工", "操作工", "服务员", "收银", "搬运", "搬运工",
            "司机", "驾驶员", "焊工", "电工", "叉车",
            "包装", "组装", "装卸", "分拣", "搬运",
            "学徒", "杂工", "清洁", "洗车", "汽修",
            "快递", "外卖", "送餐", "物流",
            "足疗", "按摩", "美容", "美发",
            "护工", "月嫂", "保姆", "钟点工",
            "促销", "地推", "发单",
            "保安员", "巡逻", "安检",
            "车工", "铣工", "钳工", "磨工", "钣金",
            "饲养", "种植", "养殖",
            "日结", "周结",
        ]
        if any(w in t for w in exclude):
            return False
        return True

    def search_keyword(self, keyword: str, page: int = 1) -> List[Dict]:
        """搜索单个关键词，返回职位列表"""
        params = {
            "keyword": keyword,
            "city": self.CITY_CODE,
            "pageIndex": page,
        }
        url = f"{self.BASE_URL}/?{urlencode(params)}"
        logger.info("[Zhaopin] Searching: keyword=%s page=%d", keyword, page)

        try:
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            logger.warning("[Zhaopin] Request failed for %s: %s", keyword, e)
            return []

        return self._parse_position_list(resp.text)

    def _parse_position_list(self, html: str) -> List[Dict]:
        """从HTML中解析__INITIAL_STATE__并提取职位列表"""
        soup = BeautifulSoup(html, "html.parser")

        for script in soup.find_all("script"):
            if not script.string or "__INITIAL_STATE__" not in script.string:
                continue

            match = re.search(
                r'__INITIAL_STATE__\s*=\s*(\{.*?\})\s*;',
                script.string, re.DOTALL
            )
            if not match:
                # __INITIAL_STATE__ may not end with semicolon
                match = re.search(
                    r'__INITIAL_STATE__\s*=\s*(\{.*\})',
                    script.string, re.DOTALL
                )
            if not match:
                continue

            try:
                state = json.loads(match.group(1))
            except json.JSONDecodeError:
                continue

            raw_list = state.get("positionList") or []
            positions = []
            for raw in raw_list:
                if not raw or not raw.get("name"):
                    continue
                pos = self._normalize_position(raw)
                if pos:
                    positions.append(pos)
            return positions

        return []

    def _normalize_position(self, raw: Dict) -> Optional[Dict]:
        """将智联原始数据标准化为统一格式"""
        title = (raw.get("name") or "").strip()
        if not title:
            return None

        # 只保留标题含技术关键词的岗位，确保数据质量
        if not self._is_relevant(title):
            return None

        company = (raw.get("companyName") or "未知公司").strip()
        city = (raw.get("workCity") or "未知").strip()

        # 薪资处理
        salary_raw = raw.get("salary60") or raw.get("salaryReal") or ""
        salary_range = _parse_salary_zh(salary_raw) or ""

        # 工作类型
        work_type_raw = raw.get("workType") or "全职"
        position_type = "全职"
        if "兼职" in work_type_raw:
            position_type = "兼职"
        elif "实习" in work_type_raw:
            position_type = "实习"

        # 学历
        edu = (raw.get("education") or "本科").strip()

        # 经验
        exp = (raw.get("workingExp") or "1-3年").strip()

        # 行业
        industry = (raw.get("industryName") or "")
        if not industry or industry == "其他":
            industry = _infer_industry(title)

        # 福利标签
        welfare = raw.get("welfareLabel") or []
        if isinstance(welfare, list):
            benefits = "、".join(welfare)
        else:
            benefits = str(welfare)

        # 技能标签
        skills = raw.get("jobSkillTags") or []
        skill_texts = []
        if isinstance(skills, list):
            for s in skills:
                if isinstance(s, dict) and s.get("name"):
                    skill_texts.append(s["name"])
        requirements = "、".join(skill_texts)

        # URL
        source_url = raw.get("positionURL") or raw.get("positionUrl") or ""

        # 发布日期
        pub_date = date.today()
        pub_str = raw.get("publishTime") or ""
        if pub_str:
            try:
                pub_date = datetime.strptime(pub_str[:10], "%Y-%m-%d").date()
            except (ValueError, IndexError):
                pass

        return {
            "title": title[:200],
            "company": company[:200],
            "location": city[:100],
            "salary_range": salary_range,
            "position_type": position_type,
            "requirements": requirements[:2000],
            "description": "",
            "benefits": benefits[:1000],
            "education": edu[:50],
            "experience": exp[:50],
            "industry": industry[:100],
            "source_url": source_url[:500],
            "published_date": pub_date,
        }

    def search_all_keywords(self, max_total: int = 500) -> List[Dict]:
        """使用多个关键词搜索，收集职位"""
        all_jobs = []
        seen_keys = set()

        for keyword in self.SEARCH_KEYWORDS:
            if len(all_jobs) >= max_total:
                break

            page = 1
            # 每页都可能被标题过滤筛掉一些，但超过 3 页后几乎没有新职位
            max_pages = 3

            while page <= max_pages and len(all_jobs) < max_total:
                jobs = self.search_keyword(keyword, page=page)
                if not jobs:
                    break

                for job in jobs:
                    if len(all_jobs) >= max_total:
                        break
                    dedup_key = (job["title"], job["company"])
                    if dedup_key not in seen_keys:
                        seen_keys.add(dedup_key)
                        all_jobs.append(job)

                logger.info(
                    "[Zhaopin] Keyword=%s page=%d got %d jobs, total=%d",
                    keyword, page, len(jobs), len(all_jobs)
                )
                page += 1
                if page <= max_pages:
                    time.sleep(random.uniform(0.5, 1.5))

        logger.info("[Zhaopin] collected %d tech jobs total", len(all_jobs))
        return all_jobs


def save_jobs_to_db(jobs: List[Dict], batch_size: int = 500) -> Dict:
    """将爬取的职位数据存入数据库"""
    try:
        from position_data.models import Position

        imported = 0
        batch = []

        for job in jobs:
            exists = Position.objects.filter(
                title=job["title"][:200],
                company=job["company"][:200],
            ).exists()
            if exists:
                continue

            pub_date = job.get("published_date") or date.today()

            batch.append(Position(
                title=job["title"][:200],
                company=job["company"][:200],
                location=job.get("location", "未知")[:100],
                salary_range=job.get("salary_range", "")[:100],
                position_type=job.get("position_type", "全职")[:20],
                requirements=job.get("requirements", ""),
                description=job.get("description", "")[:2000],
                benefits=job.get("benefits", "")[:1000],
                education=job.get("education", "本科")[:50],
                experience=job.get("experience", "1-3年")[:50],
                industry=job.get("industry", "互联网/IT")[:100],
                source_url=job.get("source_url", "")[:500],
                published_date=pub_date,
            ))

            if len(batch) >= batch_size:
                Position.objects.bulk_create(batch, ignore_conflicts=True)
                imported += len(batch)
                batch = []

        if batch:
            Position.objects.bulk_create(batch, ignore_conflicts=True)
            imported += len(batch)

        return {
            "success": True,
            "imported": imported,
            "message": f"Imported {imported} job records",
        }
    except Exception as e:
        logger.error("[DB] save error: %s", e)
        return {"success": False, "imported": 0, "message": f"Save failed: {e}"}


def run_full_scrape(max_total: int = 500) -> Dict:
    """
    执行完整爬取流程：采集 -> 保存到数据库

    Args:
        max_total: 最大采集总数

    Returns:
        {"success": bool, "total_collected": int, "total_imported": int, "message": str}
    """
    start_time = datetime.now()

    logger.info("=" * 50)
    logger.info("Starting job data scraping from Zhaopin (zhaopin.com)")
    logger.info("Target: %d jobs", max_total)

    scraper = ZhaopinScraper()
    jobs = scraper.search_all_keywords(max_total=max_total)

    elapsed_search = (datetime.now() - start_time).total_seconds()

    if not jobs:
        return {
            "success": False,
            "total_collected": 0,
            "total_imported": 0,
            "message": "No job data collected from Zhaopin",
            "elapsed_seconds": round(elapsed_search, 1),
        }

    result = save_jobs_to_db(jobs)
    total_elapsed = (datetime.now() - start_time).total_seconds()

    logger.info(
        "Scrape done: %d collected, %d imported, %.1fs",
        len(jobs), result['imported'], total_elapsed
    )
    logger.info("=" * 50)

    return {
        "success": result["success"],
        "total_collected": len(jobs),
        "total_imported": result["imported"],
        "message": f"Collected {len(jobs)}, imported {result['imported']} new records",
        "elapsed_seconds": round(total_elapsed, 1),
    }
