import difflib
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from utils import fetch_github_api, set_github_token

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    logger.error("Env Variable GITHUB_TOKEN not set, exiting..")
    sys.exit(1)
set_github_token(GITHUB_TOKEN)

USERNAME = "cjc7373"

data = []
page = 1
while True:
    logger.info(f"Reading page {page}")
    r = fetch_github_api("get", f"users/{USERNAME}/starred?per_page=100&page={page}")
    page += 1
    if not r:
        break
    for item in r:
        data.append(f"[{item['full_name']}]({item['html_url']})\n")
# print(data)

prev_file = Path("prev.txt")
prev_file.touch(exist_ok=True)
with open(prev_file, "r") as f:
    prev_data = [i for i in f.readlines()]

logger.info("Computing diffs..")
added = []
deleted = []
diffs = difflib.Differ().compare(prev_data, data)
for line in diffs:
    """
    `line` is a str and ends with '\n'
    """
    if line.startswith("  "):
        continue
    elif line.startswith("+ "):
        added.append("-" + line[1:])
    elif line.startswith("- "):
        deleted.append(line)
    else:
        # Lines beginning with ‘?’ attempt to guide the eye to intraline differences,
        # and were not present in either input sequence.
        # https://docs.python.org/3/library/difflib.html?highlight=difflib#difflib.Differ
        # So we can safely ignore these lines
        continue

if added or deleted:
    # we don't need to update if nothing changes
    with open(prev_file, "w") as f:
        logger.info(f"Updating {prev_file}")
        f.writelines(data)

    readme_file = Path("README.md")
    readme_file.touch(exist_ok=True)
    with open(readme_file, "r+") as f:
        logger.info(f"Updating {readme_file}")
        # Note when read is done, the stream position is at the end of the file
        old_content = f.read()
        date_str = datetime.now().date().isoformat()
        added_str = "Added:\n" + "".join(added) + "\n\n" if added else ""
        deleted_str = "Deleted:\n" + "".join(deleted) + "\n\n" if deleted else ""
        new_content = f"## {date_str}\n\n{added_str}{deleted_str}" + old_content
        f.seek(0)
        f.write(new_content)
else:
    logger.info("Nothing to do, exiting..")
