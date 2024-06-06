import random
import re
import sys

dice_re = re.compile(r"^\d+d\d+(\+\d+d\d+)*$")

if len(sys.argv) == 1:
    print(
        f"""usage: python {sys.argv[0]} <dice>

<dice> example: 1d6, 2d4+1d5
"""
    )
    sys.exit(0)

if not dice_re.match(sys.argv[1]):
    print("not a valid dice string")
    sys.exit(0)

# a dice would be [1, 20] as 1d20
dices = [[int(num) for num in dice.split("d")] for dice in sys.argv[1].split("+")]
res = []
for dice in dices:
    for _ in range(dice[0]):
        res.append(random.randint(1, dice[1]))

res_str = map(lambda i: str(i), res)
print(f"{sum(res)} ({','.join(res_str)})")
