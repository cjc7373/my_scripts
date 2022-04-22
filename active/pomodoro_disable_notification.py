#!/usr/bin/env python
import dbus
import time
import sys
from datetime import datetime, timedelta
from rich import print  # override built-in print
from rich.progress import track
from rich.console import Console

console = Console()

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


def render_progress(text: str, duration: timedelta):
    """Note this function will block"""
    secs = int(duration.total_seconds())
    now = datetime.now()
    print(f"{now.isoformat(' ', timespec='minutes')}: {text}")
    for n in track(range(secs), description=text):
        time.sleep(1)
    end = datetime.now()
    print(f"{end - now} elapsed")
    print(end="\a")  # beep!
    sys.stdout.flush()  # Otherwise the beep will be triggered after the sleep


if __name__ == "__main__":
    while True:
        arg_0 = inhbit()
        render_progress("Start working..", timedelta(minutes=25))
        uninhibit(arg_0)
        render_progress("Start resting..", timedelta(minutes=5))
        input("Press Enter to confirm next cycle...")
        print()
