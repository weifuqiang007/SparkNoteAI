import re
from fastapi import Request


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def parse_user_agent(user_agent: str) -> dict:
    result = {
        "device_type": "desktop",
        "browser": "Unknown",
        "os": "Unknown",
    }

    if re.search(r"Mobile|Android|iPhone|iPad", user_agent):
        if re.search(r"iPad", user_agent):
            result["device_type"] = "tablet"
        else:
            result["device_type"] = "mobile"

    if re.search(r"Edg/", user_agent):
        result["browser"] = "Edge"
    elif re.search(r"Chrome/", user_agent):
        result["browser"] = "Chrome"
    elif re.search(r"Safari/", user_agent):
        result["browser"] = "Safari"
    elif re.search(r"Firefox/", user_agent):
        result["browser"] = "Firefox"
    elif re.search(r"MSIE|Trident/", user_agent):
        result["browser"] = "Internet Explorer"

    if re.search(r"Windows", user_agent):
        result["os"] = "Windows"
    elif re.search(r"Mac OS X", user_agent):
        result["os"] = "macOS"
    elif re.search(r"Linux", user_agent):
        result["os"] = "Linux"
    elif re.search(r"iOS", user_agent):
        result["os"] = "iOS"
    elif re.search(r"Android", user_agent):
        result["os"] = "Android"

    return result


def generate_device_name(browser: str, os_name: str, device_type: str) -> str:
    if device_type == "mobile":
        return f"{browser} on Mobile"
    elif device_type == "tablet":
        return f"{browser} on Tablet"
    return f"{browser} on {os_name}"


def get_location_from_ip(ip_address: str) -> str:
    if ip_address.startswith("192.168.") or ip_address.startswith("10.") or ip_address.startswith("172."):
        return "本地网络"
    return "未知位置"
