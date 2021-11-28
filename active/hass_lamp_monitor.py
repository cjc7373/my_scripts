"""
Make lamp on and off according to my laptop screen on and off.
"""

import subprocess
import time
import re

last_status = None

while True:
    r = subprocess.run(["xset", "q"], text=True, capture_output=True)
    print(r.stdout)
    print(r.stderr)
    status = re.search(r"Monitor is (\w*)", r.stdout).group(1)
    if not last_status:
        last_status = status
    elif last_status != status:
        subprocess.run(
            "hass-cli --server http://192.168.122.159:8123 --token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJkMThlNDc2OGY0OWU0YzdlYTg2MjU5NmQ3NjMxYTFkYSIsImlhdCI6MTYyOTI3NjAwMCwiZXhwIjoxOTQ0NjM2MDAwfQ.6kqBxK2mS5U8v5xyjs3visr2CPTFIJCWhKtTKUMEH8E state toggle light.lamp1_cloud_017051",
            shell=True,
        )
        last_status = status

    time.sleep(10)
