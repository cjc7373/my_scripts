#!/usr/bin/env python
import dbus
import time
from datetime import datetime

notify_interface = dbus.Interface(
    object=dbus.SessionBus().get_object(
        "org.freedesktop.Notifications", "/org/freedesktop/Notifications"
    ),
    dbus_interface="org.freedesktop.Notifications",
)


def inhbit() -> int:
    """Inhibit (String desktop_entry, String reason, Dict of {String, Variant} hints) ↦ (UInt32 arg_0)"""
    ret = notify_interface.Inhibit("", "Entering pomodoro mode", {})
    return ret


def uninhibit(arg_0: int) -> None:
    """UnInhibit (UInt32 arg_0) ↦ ()"""
    notify_interface.UnInhibit(arg_0)


if __name__ == "__main__":
    while True:
        now = datetime.now()
        print(f"{now.isoformat(timespec='minutes')}: Start working..")
        arg_0 = inhbit()
        time.sleep(25 * 60)
        print(end="\a")  # beep!
        end = datetime.now()
        print(f"{end - now} elapsed")
        print(f"{end.isoformat(timespec='minutes')}: Start resting..")
        uninhibit(arg_0)
        print(end="\a")  # beep!
        input("Press Enter to confirm next cycle...")
        time.sleep(5 * 60)
