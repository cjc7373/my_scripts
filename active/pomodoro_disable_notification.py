#!/usr/bin/env python
import dbus
import time
import sys
import subprocess
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


if __name__ == "__main__":
    while True:
        arg_0 = inhbit()
        render_progress("Start working..", timedelta(minutes=25))
        uninhibit(arg_0)
        # print(end="\a") will not work with rich..
        # So I choose to send a notifiction instead.
        notify("Time to take a break!")
        render_progress("Start resting..", timedelta(minutes=5))
        input("Press Enter to confirm next cycle...")
        notify("Time to work again!")
        print()
