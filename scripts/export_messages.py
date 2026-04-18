# ============================================================
# WXCRAWL - Export Tin Nh???n
# ============================================================
# Xu???t tin nh???n theo cu???c tr?? chuy???n v???i t??n ng?????i g???i
# ============================================================

import json
import os
import sys
import sqlite3
import re
from datetime import datetime, timedelta

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
CONFIG_PATH = os.path.join(PROJECT_DIR, "config.json")
DECRYPT_DIR = os.path.join(PROJECT_DIR, "export", "decrypted")
EXPORT_DIR = os.path.join(PROJECT_DIR, "export", "messages")
LOG_DIR = os.path.join(PROJECT_DIR, "logs")


def log(msg):
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, "export_messages.log")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class ContactResolver:
    def __init__(self, micromsg_path):
        self.contacts = {}
        self.chatrooms = {}
        self._load(micromsg_path)

    def _load(self, micromsg_path):
        try:
            conn = sqlite3.connect(micromsg_path)
            cur = conn.cursor()
            cur.execute("SELECT UserName, NickName, Remark FROM Contact")
            for username, nickname, remark in cur.fetchall():
                name = remark.strip() if remark and remark.strip() else (nickname or username)
                self.contacts[username] = {
                    "nickname": nickname or "",
                    "remark": remark or "",
                    "display_name": name
                }
            cur.execute("SELECT ChatRoomName, UserNameList FROM ChatRoom")
            for roomname, userlist in cur.fetchall():
                members = userlist.split("^G") if userlist else []
                self.chatrooms[roomname] = members
            conn.close()
            log(f"Loaded {len(self.contacts)} contacts, {len(self.chatrooms)} chatrooms")
        except Exception as e:
            log(f"Error loading contacts: {e}")

    def get_name(self, wxid):
        if wxid in self.contacts:
            info = self.contacts[wxid]
            return info["remark"] if info["remark"] else info["nickname"] or wxid
        return wxid

    def get_member_name(self, wxid):
        return self.get_name(wxid)

    def is_chatroom(self, wxid):
        return wxid in self.chatrooms or wxid.endswith("@chatroom")


def extract_sender(bytes_extra):
    if not bytes_extra:
        return None
    try:
        data = bytes_extra if isinstance(bytes_extra, bytes) else bytes_extra.encode('latin-1')
        matches = re.findall(rb'wxid_[a-zA-Z0-9]+', data)
        return matches[0].decode('utf-8') if matches else None
    except:
        return None


def extract_media(content):
    media = {"type": None, "md5": None, "width": None, "height": None}
    if not content or not content.strip().startswith("<?xml"):
        return media
    try:
        img = re.search(r'<img[^>]*>', content)
        if img:
            tag = img.group(0)
            media["type"] = "image"
            m = re.search(r'md5="([^"]*)"', tag)
            media["md5"] = m.group(1) if m else None
            w = re.search(r'cdnthumbwidth="([^"]*)"', tag)
            h = re.search(r'cdnthumbheight="([^"]*)"', tag)
            media["width"] = int(w.group(1)) if w else None
            media["height"] = int(h.group(1)) if h else None
    except:
        pass
    return media


def format_msg(record, resolver, my_wxid):
    ct = record.get("CreateTime", 0) or 0
    try:
        dt_str = datetime.fromtimestamp(ct).strftime("%Y-%m-%d %H:%M:%S") if ct else "unknown"
    except:
        dt_str = str(ct)

    content = record.get("StrContent", "") or ""
    if isinstance(content, bytes):
        content = content.decode('utf-8', errors='ignore')

    talker = record.get("StrTalker", "") or ""
    is_sender = record.get("IsSender", 0)
    bytes_extra = record.get("BytesExtra", b"") or b""

    sender_wxid = None
    sender_name = None
    if resolver.is_chatroom(talker):
        sender_wxid = extract_sender(bytes_extra)
        if sender_wxid == my_wxid:
            sender_name = "Me"
        else:
            sender_name = resolver.get_member_name(sender_wxid) if sender_wxid else "Unknown"
    else:
        sender_name = "Me" if is_sender else resolver.get_name(talker)

    return {
        "msg_id": record.get("localId", "") or "",
        "talker_id": talker,
        "talker_name": resolver.get_name(talker),
        "is_chatroom": resolver.is_chatroom(talker),
        "sender_id": sender_wxid or (talker if not resolver.is_chatroom(talker) else None),
        "sender_name": sender_name,
        "msg_type": record.get("Type", 0) or 0,
        "content": content,
        "content_preview": content[:100] + "..." if len(content) > 100 else content,
        "create_time": ct,
        "datetime": dt_str,
        "is_from_me": bool(is_sender),
        "media": extract_media(content),
    }


def read_messages(db_path, days=30):
    results = []
    cutoff = int((datetime.now() - timedelta(days=days)).timestamp())
    try:
        conn = sqlite3.connect(db_path)
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        msg_table = "MSG" if "MSG" in tables else ("ChatMsg" if "ChatMsg" in tables else None)
        if msg_table:
            cols = [d[0] for d in conn.execute(f"SELECT * FROM {msg_table} LIMIT 0").description]
            tc = "CreateTime" if "CreateTime" in cols else "createTime"
            try:
                rows = conn.execute(f"SELECT * FROM {msg_table} WHERE {tc} > ? ORDER BY {tc} DESC", (cutoff,)).fetchall()
            except:
                rows = conn.execute(f"SELECT * FROM {msg_table}").fetchall()
            for row in rows:
                results.append(dict(zip(cols, row)))
        conn.close()
    except Exception as e:
        log(f"Error reading {db_path}: {e}")
    return results


def sanitize(name):
    return re.sub(r'[<>:"/\\|?*]', '_', str(name))[:50].strip()


def export_json(data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    log("=" * 50)
    log("EXPORT MESSAGES - WXCRAWL")
    log("=" * 50)

    config = load_config()
    key = config.get("key", "").strip()
    if not key:
        log("ERROR: No key in config.json")
        log("Run: python scripts/get_key.py")
        return

    micromsg_path = os.path.join(DECRYPT_DIR, "de_MicroMsg.db")
    if not os.path.exists(micromsg_path):
        log(f"ERROR: Run decrypt_db.py first")
        return

    resolver = ContactResolver(micromsg_path)
    my_wxid = config.get("wxid", "")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    individual_dir = os.path.join(EXPORT_DIR, f"individual_{ts}")
    os.makedirs(individual_dir, exist_ok=True)

    all_msgs = []
    msg0_path = os.path.join(DECRYPT_DIR, "Multi", "de_MSG0.db")
    if os.path.exists(msg0_path):
        msgs = read_messages(msg0_path, days=30)
        log(f"Read {len(msgs)} messages from MSG0.db")
        all_msgs.extend(msgs)

    formatted = [format_msg(m, resolver, my_wxid) for m in all_msgs]

    grouped = {}
    for msg in formatted:
        t = msg.get("talker_id", "unknown")
        if t not in grouped:
            grouped[t] = []
        grouped[t].append(msg)

    log(f"Total: {len(grouped)} conversations, {len(formatted)} messages")

    files = []
    for talker_id, messages in grouped.items():
        name = resolver.get_name(talker_id)
        is_cr = resolver.is_chatroom(talker_id)
        filename = f"{sanitize(name)}_{talker_id[:15]}.json"
        filepath = os.path.join(individual_dir, filename)
        export_json({
            "conversation_id": talker_id,
            "conversation_name": name,
            "is_chatroom": is_cr,
            "type": "Nh??m" if is_cr else "C?? nh??n",
            "total_messages": len(messages),
            "messages": messages
        }, filepath)
        files.append({"filename": filename, "name": name, "type": "Nh??m" if is_cr else "C?? nh??n", "messages": len(messages)})
        log(f"  Exported: {filename}")

    export_json({"export_time": ts, "total_conversations": len(grouped), "total_messages": len(formatted), "files": files},
                os.path.join(EXPORT_DIR, f"summary_{ts}.json"))

    log(f"\n{'='*50}")
    log(f"DONE! {len(files)} conversations exported")
    log(f"Location: {individual_dir}")
    log(f"{'='*50}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"FATAL ERROR: {e}")
        sys.exit(1)
