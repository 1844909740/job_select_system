"""
爬取招聘网站职位数据的管理命令
用法: python manage.py scrape_jobs [--max-total 500]
"""
from django.core.management.base import BaseCommand
from position_data.job_scraper import run_full_scrape


class Command(BaseCommand):
    help = '从招聘网站爬取职位数据 (We Work Remotely)'

    def add_arguments(self, parser):
        parser.add_argument('--max-total', type=int, default=500,
                          help='最大采集总数（默认500）')

    def handle(self, *args, **options):
        self.stdout.write('Starting job scraping from We Work Remotely...')
        result = run_full_scrape(max_total=options.get('max_total', 500))

        if result['success']:
            self.stdout.write(self.style.SUCCESS(result['message']))
        else:
            self.stdout.write(self.style.WARNING(result['message']))

        self.stdout.write(f"Time: {result.get('elapsed_seconds', 0)}s")
