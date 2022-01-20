"""
It's very useful when I want to use my Surface to heat my hands.
"""
from multiprocessing import cpu_count, Process, current_process
import time
import signal
import sys


def handle_sigterm(signum, frame):
    print(f"Exiting process {current_process()}")
    sys.exit(0)


signal.signal(signal.SIGINT, handle_sigterm)


def dumb_task():
    print(f"Spawning process {current_process()}")
    x = 0
    while True:
        x += 1


if __name__ == "__main__":
    pool_size = cpu_count() - 1
    for _ in range(pool_size):
        p = Process(target=dumb_task)
        p.start()
    start = time.time()
    time.sleep(0.5)  # wait all the processes to start
    while True:
        print(f"Running {int(time.time() - start)}s", end="")
        print("\033[A")
        time.sleep(1)
