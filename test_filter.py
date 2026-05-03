"""Test with title filter"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from position_data.job_scraper import ZhaopinScraper

s = ZhaopinScraper()
total = 0
for kw in s.SEARCH_KEYWORDS:
    jobs = s.search_keyword(kw, page=1)
    total += len(jobs)
    if jobs:
        for j in jobs[:3]:
            print(f'{kw:8s} | {j["title"][:35]:35s} | {j["salary_range"]:8s} | {j["company"][:15]:15s}')
        if len(jobs) > 3:
            print(f'  ... and {len(jobs)-3} more')
    else:
        print(f'{kw:8s} | (no matching jobs)')
    print()
print(f'Total: {total} jobs across all keywords (page 1 only)')
