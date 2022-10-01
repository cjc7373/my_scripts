import psutil
import time
import sys
import matplotlib.pyplot as plt

data_file = "fan.data"

# print(sys.argv)

if len(sys.argv) == 1:
    f = open(data_file, "a")
    while True:
        cpu_load = psutil.cpu_percent()
        temp = psutil.sensors_temperatures()["coretemp"][0].current
        f.write(f"{int(time.time())}, {cpu_load}, {temp}\n")
        time.sleep(1)
else:
    d_time = []
    d_load = []
    d_temp = []
    with open(data_file, "r") as f:
        for line in f:
            t, load, temp = [float(i) for i in line.split(",")]
            d_time.append(int(t))
            d_load.append(load)
            d_temp.append(temp)
    fig, ax = plt.subplots()
    ax.plot(d_temp, color="blue")
    ax.set_ylabel("Temperature", color="blue")

    ax.plot(d_load, color="red")

    # ax2 = ax.twinx()
    # ax2.plot(d_load, color="red")
    # ax2.set_ylabel("Load", color="red")

    plt.show()
