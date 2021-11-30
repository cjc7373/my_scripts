"""
统计 Github 上自己所有 commits 的时间分布.
"""
import requests
from datetime import datetime

statistic = [0 for i in range(24)]
all_cnt = 0

page = 1
while True:
    url = f"https://api.github.com/search/commits?q=author:cjc7373&per_page=100&page={page}"
    print(f"Reading page {page}")
    r = requests.get(url)
    items = r.json()["items"]

    page += 1
    if not items:
        break

    for item in items:
        date_str = item["commit"]["committer"]["date"]
        # print(date_str)
        try:
            t = datetime.fromisoformat(date_str)
        except ValueError as e:
            # may encounter something like 2021-02-11T08:55:12.000Z
            print(e)
        # print(t.hour)
        statistic[t.hour] += 1
        all_cnt += 1

statistic = [i * 200 // all_cnt for i in statistic]
for index, data in enumerate(statistic):
    print(f"{index:2} - {index+1:2}: ", end="")
    for i in range(data):
        print("▇", end="")
    print()
