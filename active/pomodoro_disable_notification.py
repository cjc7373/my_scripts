#!/usr/bin/env python
"""
A simple pomodoro timer, which utilizes org.freedesktop.Notifications dbus interface.
"""
import argparse
import pickle
import subprocess
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import dbus
import numpy as np
from rich import print  # override built-in print
from rich.console import Console
from rich.progress import Progress, track

console = Console()
new_data: list[datetime] = []
WORKING_DIR = Path(__file__).resolve().parent

notify_interface = dbus.Interface(
    object=dbus.SessionBus().get_object(
        "org.freedesktop.Notifications", "/org/freedesktop/Notifications"
    ),
    dbus_interface="org.freedesktop.Notifications",
)


def inhbit() -> int:
    """Inhibit (String desktop_entry, String reason, Dict of {String, Variant} hints) -> (UInt32 arg_0)"""
    ret = notify_interface.Inhibit("", "Entering pomodoro mode", {})
    return ret


def uninhibit(arg_0: int) -> None:
    """UnInhibit (UInt32 arg_0) -> ()"""
    notify_interface.UnInhibit(arg_0)


def notify(message: str) -> None:
    # FIXME: hints like `"sound-file": "/usr/share/sounds/Oxygen-Sys-App-Error.ogg"`
    # is not working. Don't know why.
    # So I have to use mpv..
    # Anyway, sound is not so much important.
    notify_interface.Notify(
        "Pomodoro",  # app_name
        0,  # replaces_id, The optional notification ID that this notification replaces
        "",  # app_icon
        message,  # summary
        "",  # body
        [],  # actions
        {},  # hints
        -1,  # expire_timeout, -1 means default
    )
    subprocess.run(
        args="mpv /usr/share/sounds/Oxygen-Sys-App-Error-Critical.ogg --script-opts=autoload-disabled=yes --volume=120",
        shell=True,
        capture_output=True,
    )


def render_progress(text: str, duration: timedelta):
    """
    Note: this function will block.

    Performance WARNING: Using rich's progress bar causes about 2% CPU usage.
    Without it, the CPU usage is nearly 0%.
    We should see if we could improve this.
    """
    secs = duration.total_seconds()
    now = datetime.now()
    print(f"{now.isoformat(' ', timespec='minutes')}: {text}")
    with Progress(auto_refresh=False) as progress:
        task = progress.add_task(text, total=secs)

        while not progress.finished:
            progress.update(task, advance=1, refresh=True)
            time.sleep(1)
    end = datetime.now()
    print(f"{end - now} elapsed\n")


def run_pomodoto():
    while True:
        arg_0 = inhbit()
        render_progress("Start working..", timedelta(minutes=25))
        new_data.append(datetime.now())
        uninhibit(arg_0)
        # print(end="\a") will not work with rich..
        # So I choose to send a notifiction instead.
        notify("Time to take a break!")
        render_progress("Start resting..", timedelta(minutes=5))
        notify("Time to work again!")
        input("Press Enter to confirm next cycle...")
        print()


def read_data() -> list[datetime]:
    """
    data 保证是有序的, 记录的是每次番茄钟的完成时间.
    """
    try:
        with open(WORKING_DIR / "pomodoro.data", "rb") as f:
            data = pickle.load(f)
    except FileNotFoundError:
        data = []
    return data


def stat(args):
    data = read_data()
    day_count = 0
    day_counts = []
    today = date.today()
    for index, dt in enumerate(data):
        output = True
        if not args.all and today - dt.date() >= timedelta(days=7):
            output = False

        day_count += 1
        if output:
            if day_count == 1:
                print(dt.date())
            t = dt.time()
            prev_t = (dt - timedelta(minutes=25)).time()
            print(
                f"{prev_t.isoformat(timespec='minutes')} - {t.isoformat(timespec='minutes')}"
            )
        if index + 1 < len(data) and dt.date() != data[index + 1].date():
            if day_count != 0:
                day_counts.append(day_count)
                if output:
                    print(f"Total: {day_count} pomodoro(s)")
                    print()
            day_count = 0
    if day_count != 0:
        day_counts.append(day_count)
        print(f"Total: {day_count} pomodoro(s)")
        print()
    else:
        print("No record in the last 7 days.")

    print(f"Mean pomodoros: {np.mean(day_counts):.2f}")
    print(f"Median pomodoros: {np.median(day_counts):.0f}")
    print(f"Max pomodoros: {np.max(day_counts)}")


def save_data():
    data = read_data()
    with open(WORKING_DIR / "pomodoro.data", "wb") as f:
        pickle.dump(data + new_data, f)
    print()
    print(f"{len(new_data)} record(s) added.")


def run(args):
    try:
        run_pomodoto()
    except KeyboardInterrupt:
        # do not print stack trace
        pass
    finally:
        save_data()


def debug(args):
    print("You typed debug!")
    notify("Time to take a break!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers()
    parser_run = subparsers.add_parser(name="run", help="run pomodoro")
    parser_run.set_defaults(func=run)

    parser_stat = subparsers.add_parser(
        name="stat", help="show the last 7 days records"
    )
    parser_stat.add_argument(
        "-a", "--all", action="store_true", help="show all records"
    )
    parser_stat.set_defaults(func=stat)

    parser_debug = subparsers.add_parser(name="debug")
    parser_debug.set_defaults(func=debug)

    args = parser.parse_args()
    if "func" in args:
        args.func(args)
    else:
        run(args)
