import re
import sys
import random

dice_re = re.compile(r"^\d+d\d+(\+\d+d\d+)*$")

if len(sys.argv) == 1:
    print(f"usage: python {sys.argv[0]} <dice>")
    sys.exit(0)

if not dice_re.match(sys.argv[1]):
    print("not a valid dice string")
    sys.exit(0)

# a dice would be [1, 20] as 1d20
dices = [[int(num) for num in dice.split("d")] for dice in sys.argv[1].split("+")]
res = 0
for dice in dices:
    for _ in range(dice[0]):
        t = random.randint(1, dice[1])
        res += t

print(res)
