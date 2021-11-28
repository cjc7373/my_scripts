"""
Replaced by Anki.
"""
import json
import os
import sys
import argparse


def save(data):
    with open("NEC_reminder_data.json", "w") as f:
        json.dump(data, f)


try:
    with open("NEC_reminder_data.json") as f:
        data = json.load(f)
except FileNotFoundError:
    all = int(input("Please enter the number of all lessons: "))
    done = int(input("Please enter the number of lessons you have already learned: "))
    data = []
    for i in range(1, all + 1):
        item = {
            "name": f"Lesson {i}",
            "is_learned": True if i <= done else False,
            "revision_count": 1 if i <= done else 0,
            "id": i,
        }
        data.append(item)
    save(data)


def learn(lesson):
    for i in data:
        if i["id"] == lesson:
            i["is_learned"] = True
            i["revision_count"] += 1
            break
    save(data)


def unlearned():
    print(f"ID    Name")
    for i in data:
        if i["is_learned"] == False:
            print(f"{i['id']} {i['name']}")


def revision_status():
    print(f"{'ID':3} {'Name':10} {'Revision Count':3}")
    for i in data:
        if i["is_learned"] == True:
            print(f"{i['id']:3} {i['name']:10} {i['revision_count']:3}")


def start_revision():
    min_revision = data[0]["revision_count"]
    min_index = 0
    for index, i in enumerate(data):
        if i["is_learned"] == True and i["revision_count"] < min_revision:
            min_revision = i["revision_count"]
            min_index = index
    print(f"You are going to revise {data[min_index]['name']}, press enter to confirm.")
    input()
    data[min_index]["revision_count"] += 1
    save(data)
    print("Done.")


parser = argparse.ArgumentParser(
    description="Remind you to revise NCE.",
    formatter_class=argparse.RawTextHelpFormatter,
)

parser.add_argument(
    "action",
    choices=("n", "u", "r", "s"),
    help="""available choices:
n <lesson>  to learn a new lesson
u           to see unlearned lessons
r           to see revision status
s           to start a revision
""",
)
parser.add_argument(dest="args", nargs="*", help="other arguments")
args = parser.parse_args()

map_ = {"n": "learn", "u": "unlearned", "r": "revision_status", "s": "start_revision"}

getattr(sys.modules["__main__"], map_[args.action])(*args.args)
