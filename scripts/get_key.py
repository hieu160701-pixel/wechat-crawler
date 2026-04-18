# ============================================================
# WXCRAWL - Lấy Key từ WeChat PC
# ============================================================
# Chạy: python scripts/get_key.py
# Yêu cầu: WeChat PC đang mở và đăng nhập
# ============================================================

import os
import sys
import json
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
CONFIG_PATH = os.path.join(PROJECT_DIR, "config.json")
LOG_DIR = os.path.join(PROJECT_DIR, "logs")


def log(msg):
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, "get_key.log")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(data):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main():
    log("=" * 50)
    log("GET KEY - WXCRAWL")
    log("=" * 50)
    log("Please ensure WeChat PC is running and logged in")
    print()

    try:
        from pywxdump import get_wx_info
        log("Getting WeChat info...")

        wx_info = get_wx_info()
        if wx_info:
            log(f"WeChat Info: {wx_info}")

            key = wx_info.get("key", "")
            wxid = wx_info.get("wxid", "")
            version = wx_info.get("version", "")

            if key:
                log(f"Key found: {key[:32]}...")

                config = load_config()
                config["key"] = key
                config["wxid"] = wxid
                config["version"] = version

                if "wx_dir" not in config:
                    wx_dirs = [
                        os.path.join(os.environ.get("USERPROFILE", ""), "Documents", "WeChat Files", wxid),
                        r"C:\Users\Public\Documents\WeChat Files",
                    ]
                    for d in wx_dirs:
                        if os.path.exists(d):
                            for item in os.listdir(d):
                                item_path = os.path.join(d, item)
                                if os.path.isdir(item_path) and "wxid" in item.lower():
                                    config["wx_dir"] = item_path
                                    break
                            if "wx_dir" not in config:
                                config["wx_dir"] = d
                            break

                save_config(config)
                log(f"Config updated: {CONFIG_PATH}")
                print()
                print("=" * 50)
                print("SUCCESS! Key obtained and saved.")
                print(f"Key: {key}")
                print(f"wxid: {wxid}")
                print("=" * 50)
            else:
                log("ERROR: No key in WeChat info")
                print("ERROR: Could not get key from WeChat")
        else:
            log("ERROR: Could not get WeChat info")
            print("ERROR: Could not connect to WeChat")

    except ImportError:
        log("ERROR: pywxdump not installed")
        print("ERROR: pywxdump not installed")
        print("Run: pip install pywxdump")
    except Exception as e:
        log(f"ERROR: {e}")
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
