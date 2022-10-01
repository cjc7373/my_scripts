# https://gitlab.com/jtaimisto/bluewalker

# temp.data is generated from:
# sudo ./go/bin/bluewalker -device hci0 -observer -mijia -duration -1 >> test/temp.txt
# sudo btmgmt --index hci0 power off

import matplotlib.pyplot as plt
import re

time: list[str] = []
data = []
humidity = []

with open("temp.data", "r") as f:
    for line in f:
        res = re.search(
            r"Temperature: (?P<temp>.*)C Humidity: (?P<humidity>.*)%  Battery", line
        )
        if res:
            # print(res.group(1))
            # print(res.group(2))
            # time.append(res.group(1))
            data.append(float(res.group("temp")))
            humidity.append(float(res.group("humidity")))

fig, ax = plt.subplots()
ax.plot(data, color="blue")
ax.set_ylabel("Temperature", color="blue")

ax2 = ax.twinx()
ax2.plot(humidity, color="red")
ax2.set_ylabel("Humidity", color="red")
# tick_interval = 30
# ax.set_xticks(range(len(time))[::tick_interval], time[::tick_interval])

plt.show()
