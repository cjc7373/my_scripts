"""
统计 Github 上自己所有 commits 的时间分布.
"""
import requests
import shutil
from datetime import datetime


def fetch_data(user: str) -> list[str]:
    page = 1
    res: list[str] = []
    while True:
        url = f"https://api.github.com/search/commits?q=author:{user}&per_page=100&page={page}"
        print(f"Reading page {page}")
        r = requests.get(url)
        items = r.json()["items"]

        page += 1
        if not items:
            return res

        for item in items:
            date_str = item["commit"]["committer"]["date"]
            # print(date_str)
            res.append(date_str)


def generate_statistic(data: list[str]) -> tuple[list[int], int]:
    statistic = [0 for i in range(24)]
    all_cnt = 0
    for date_str in data:
        try:
            t = datetime.fromisoformat(date_str)
        except ValueError as e:
            # may encounter something like 2021-02-11T08:55:12.000Z
            print(f"WARNING: {e}")
        # print(t.hour)
        statistic[t.hour] += 1
        all_cnt += 1
    return statistic, all_cnt


def print_result(statistic, all_cnt):
    terminal_width, _ = shutil.get_terminal_size((80, 24))
    scale = (terminal_width - 10) / max(statistic)
    statistic = [int(i * scale) for i in statistic]
    for index, data in enumerate(statistic):
        print(f"{index:2} - {index+1:2}: ", end="")
        for i in range(data):
            print("▇", end="")
        print()
    # 打印横坐标, 间距为 10
    print("Commits: ", end="")
    for i in range(0, (terminal_width - 10), 10):
        print(f"{int(i/scale):<10}", end="")
    print()


if __name__ == "__main__":
    data = fetch_data("cjc7373")
    statistic, all_cnt = generate_statistic(data)
    # print(statistic, all_cnt)
    print_result(statistic, all_cnt)
