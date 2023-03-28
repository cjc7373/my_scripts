from prometheus_client import start_http_server, Gauge
import prometheus_client
import random
import time
import os
import miniflux

# disable default collector metrics
prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)

counter = Gauge("miniflux_counter", "read/unread entries counter", ["feed", "status"])
client = miniflux.Client(
    "https://rss.coherence.space/",
    api_key=os.environ["MINIFLUX_APIKEY"],
)


def fetch_miniflux_data():
    counters = client.get_feed_counters()
    feeds = client.get_feeds()

    feed_map = {feed["id"]: feed["title"] for feed in feeds}
    res = {}
    for entry in counters:
        if entry == "reads":
            status = "read"
        elif entry == "unreads":
            status = "unread"
        res[status] = {
            feed_map[int(feed_id)]: count for feed_id, count in counters[entry].items()
        }
    # example res:
    #     {'reads': {'Adventures in Linux and KDE': 9,
    #            'KDE Community': 9,
    #            'Miniflux release notes': 1,
    #            'Release notes from gitea': 7,
    #            'The Django weblog': 5,
    #            'This Week in Rust': 8,
    #            'Visual Studio Code - Code Editing. Redefined.': 1,
    #            'taoky’s blog': 1,
    #            "依云's Blog": 2,
    #            '李辉': 3,
    #            '知识分子的知乎文章': 21},
    #  'unreads': {'Adventures in Linux and KDE': 1,
    #              'KDE Community': 1,
    #              'This Week in Rust': 1,
    #              'Visual Studio Code - Code Editing. Redefined.': 2,
    #              'iBug': 3,
    #              'taoky’s blog': 2,
    #              '知识分子的知乎文章': 76,
    #              '阮一峰的网络日志': 22}}
    return res


def process_request(t):
    res = fetch_miniflux_data()
    for status in res:
        for entry in res[status]:
            counter.labels(feed=entry, status=status).set(res[status][entry])
    time.sleep(10)


if __name__ == "__main__":
    # Start up the server to expose the metrics.
    start_http_server(8123)
    # Generate some requests.
    while True:
        process_request(10)
