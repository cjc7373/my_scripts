#!/usr/bin/env python
"""
A simple pomodoro timer, which utilizes org.freedesktop.Notifications dbus interface.
"""
import dbus
import time
import subprocess
import argparse
import pickle
import threading
import signal
import sys
from datetime import datetime, timedelta, date
from pathlib import Path
from rich import print  # override built-in print
from rich.progress import track
from rich.console import Console

console = Console()
new_data = []
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
        args="mpv /usr/share/sounds/Oxygen-Sys-App-Error-Critical.ogg --script-opts=autoload-disabled=yes",
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
    secs = int(duration.total_seconds())
    now = datetime.now()
    print(f"{now.isoformat(' ', timespec='minutes')}: {text}")
    for _ in track(range(secs), description=text):
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


def stat():
    data = read_data()
    day_count = 0
    prev_date = date.today()
    for dt in data:
        if prev_date != dt.date():
            if day_count != 0:
                print(f"Total: {day_count} pomodoro(s)")
                print()
            day_count = 0
            prev_date = dt.date()
            print(dt.date())
        day_count += 1
        t = dt.time()
        prev_t = (dt - timedelta(minutes=25)).time()
        print(
            f"{prev_t.isoformat(timespec='minutes')} - {t.isoformat(timespec='minutes')}"
        )
    if day_count != 0:
        print(f"Total: {day_count} pomodoro(s)")
        print()


def handle_sigint(signum, frame):
    for th in threading.enumerate():
        # import traceback
        # print(th)
        # traceback.print_stack(sys._current_frames()[th.ident])
        if th != threading.main_thread():
            # A hack to the rich library
            # to make the threads drawing the progress bar exit
            th.done.set()
            th.join()
    # FIXME: 解决进度条在文字之下
    sys.stdout.buffer.flush()
    data = read_data()
    with open(WORKING_DIR / "pomodoro.data", "wb") as f:
        pickle.dump(data + new_data, f)
    print()
    print(f"{len(new_data)} record(s) added.")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_sigint)

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "action",
        choices=["run", "stat"],
        nargs="?",
        default="run",
        help="run: run the pomodoro\nstat: show statistics\n (default: %(default)s)",
    )
    args = parser.parse_args()
    if args.action == "run":
        run_pomodoto()
    else:
        stat()
