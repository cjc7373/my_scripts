"""
SHA-256 algorithm implementation.
The implementation refers to: https://en.wikipedia.org/wiki/SHA-2#Pseudocode
STATUS: abandoned
"""
import sys

h = [
    0x6A09E667,
    0xBB67AE85,
    0x3C6EF372,
    0xA54FF53A,
    0x510E527F,
    0x9B05688C,
    0x1F83D9AB,
    0x5BE0CD19,
]

k = [
    0x428A2F98,
    0x71374491,
    0xB5C0FBCF,
    0xE9B5DBA5,
    0x3956C25B,
    0x59F111F1,
    0x923F82A4,
    0xAB1C5ED5,
    0xD807AA98,
    0x12835B01,
    0x243185BE,
    0x550C7DC3,
    0x72BE5D74,
    0x80DEB1FE,
    0x9BDC06A7,
    0xC19BF174,
    0xE49B69C1,
    0xEFBE4786,
    0x0FC19DC6,
    0x240CA1CC,
    0x2DE92C6F,
    0x4A7484AA,
    0x5CB0A9DC,
    0x76F988DA,
    0x983E5152,
    0xA831C66D,
    0xB00327C8,
    0xBF597FC7,
    0xC6E00BF3,
    0xD5A79147,
    0x06CA6351,
    0x14292967,
    0x27B70A85,
    0x2E1B2138,
    0x4D2C6DFC,
    0x53380D13,
    0x650A7354,
    0x766A0ABB,
    0x81C2C92E,
    0x92722C85,
    0xA2BFE8A1,
    0xA81A664B,
    0xC24B8B70,
    0xC76C51A3,
    0xD192E819,
    0xD6990624,
    0xF40E3585,
    0x106AA070,
    0x19A4C116,
    0x1E376C08,
    0x2748774C,
    0x34B0BCB5,
    0x391C0CB3,
    0x4ED8AA4A,
    0x5B9CCA4F,
    0x682E6FF3,
    0x748F82EE,
    0x78A5636F,
    0x84C87814,
    0x8CC70208,
    0x90BEFFFA,
    0xA4506CEB,
    0xBEF9A3F7,
    0xC67178F2,
]


def pad(msg: bytearray) -> bytearray:
    msg_len = len(msg) * 8
    msg.append(0x80)  # a single '1' bit and '0's
    while not (len(msg) * 8 + 64) % 512 == 0:
        msg.append(0x00)
    msg += bytearray(
        msg_len.to_bytes(8, "big")
    )  # append the length of the message in 64 bits
    assert (len(msg) * 8) % 512 == 0
    return msg


def process_chunk(chuck: bytearray) -> bytearray:
    ...


if __name__ == "__main__":
    message = ""
    for line in sys.stdin:
        message += line
    message.strip("\n")
    # message 总是为整数个字节
    msg_bytearray = bytearray(message.encode())
    msg_bytearray = pad(msg_bytearray)
    for i in msg_bytearray:
        print(i, end=" ")
    print()
    print(message)
    cur = 0
