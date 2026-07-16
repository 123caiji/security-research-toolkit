import requests
import re
import base64
import socket
import ssl

requests.packages.urllib3.disable_warnings()

HOST = "119.29.238.216"
TIMEOUT = 15

FLAGS_FOUND = []


def add_flag(location, content, method=""):
    FLAGS_FOUND.append({"location": location, "content": content, "method": method})
    print(f"\n  🚩 发现FLAG! [{method}]")
    print(f"     位置: {location}")
    print(f"     内容: {content}")


def check_flag_pattern(text):
    if not text:
        return None
    patterns = [
        r'flag\{[^}]+\}',
        r'FLAG\{[^}]+\}',
        r'ctf\{[^}]+\}',
        r'CTF\{[^}]+\}',
        r'key\{[^}]+\}',
        r'secret\{[^}]+\}',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            return match