# ============================================================
# WXCRAWL - Giải mã Database
# ============================================================
# Yêu cầu: WeChat PC đang mở, pywxdump đã cài
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
DECRYPT_DIR = os.path.join(PROJECT_DIR, "export", "decrypted")
LOG_DIR = os.path.join(PROJECT_DIR, "logs")


def log(msg):
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, "decrypt.log")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    log("=" * 50)
    log("DECRYPT DATABASE - WXCRAWL")
    log("=" * 50)

    config = load_config()
    key = config.get("key", "").strip()
    wx_dir = config.get("wx_dir", "")

    if not key:
        log("ERROR: No key in config.json")
        log("Run: python scripts/get_key.py")
        return

    log(f"WeChat Directory: {wx_dir}")
    log(f"Key: {key[:16]}...")

    os.makedirs(DECRYPT_DIR, exist_ok=True)
    os.makedirs(os.path.join(DECRYPT_DIR, "Multi"), exist_ok=True)

    try:
        from pywxdump import decrypt_merge
    except ImportError:
        log("ERROR: pywxdump not installed")
        return

    # Decrypt MicroMsg.db
    micromsg_src = os.path.join(wx_dir, "Msg", "MicroMsg.db")
    if os.path.exists(micromsg_src):
        log(f"Decrypting: MicroMsg.db")
        try:
            decrypt_merge(key, micromsg_src, DECRYPT_DIR)
            log(f"  Success: de_MicroMsg.db")
        except Exception as e:
            log(f"  Error: {e}")

    # Decrypt MSG0.db
    msg_src = os.path.join(wx_dir, "Msg", "Multi", "MSG0.db")
    if os.path.exists(msg_src):
        log(f"Decrypting: MSG0.db")
        try:
            decrypt_merge(key, msg_src, os.path.join(DECRYPT_DIR, "Multi"))
            log(f"  Success: de_MSG0.db")
        except Exception as e:
            log(f"  Error: {e}")

    log(f"\n{'='*50}")
    log(f"Decryption complete!")
    log(f"Output: {DECRYPT_DIR}")
    log(f"{'='*50}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"FATAL ERROR: {e}")
        sys.exit(1)
