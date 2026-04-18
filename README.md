================================================================================
WXCRAWL - WeChat PC Data Crawler
Version: 1.0.0
================================================================================

DESCRIPTION
-----------
Automatic tool to export WeChat PC (Windows) messages into individual JSON files.
Each conversation is exported separately with sender names resolved.

================================================================================
IMPORTANT NOTICES
================================================================================

1. CONFIDENTIAL: Master Key in config.json is strictly confidential.
   Do NOT share with anyone.

2. LEGAL: Only use for backing up your own account data.
   Unauthorized use may violate laws.

3. SECURITY: config.json is in .gitignore and will not be pushed to git.

================================================================================
SYSTEM REQUIREMENTS
================================================================================

1. Python 3.10 or higher
   - Download: https://www.python.org/downloads/

2. WeChat PC installed and running
   - IMPORTANT: Supports WeChat versions 3.9.x - 4.0.x (WeChat.exe)
   - WeChat 4.1+ uses WeChatAppEx.exe and CANNOT auto-get key yet
   - If you have WeChat 4.1+, see DOWNGRADE section below

3. pywxdump 3.1+
   - Install: pip install pywxdump

================================================================================
DOWNGRADE WECHAT (Required for WeChat 4.1+ Users)
================================================================================

WeChat 4.1+ does NOT expose encryption key in memory, so this tool cannot
auto-get the key. You must use WeChat 3.9.x - 4.0.x.

How to downgrade:
1. Uninstall current WeChat from Control Panel
2. Download older version from: https://github.com/tom-snow/wechat-windows-versions
3. Install version 3.9.5.33 or 4.0.0.x
4. DO NOT auto-update WeChat after installation
5. Disable WeChat auto-update in settings

Note: Your chat history will NOT be deleted when downgrading.

================================================================================
SETUP
================================================================================

Step 1: Install pywxdump
------------------------
Open CMD and run:
    pip install pywxdump

Step 2: Get Key
---------------
    cd C:\path\to\Wxcrawl
    python scripts\get_key.py

IMPORTANT: WeChat PC must be running and logged in.

Step 3: Verify config.json
-------------------------
Check that config.json contains:
    - "key": "xxxxx" (auto-filled)
    - "wxid": "wxid_xxx" (auto-filled)
    - "wx_dir": "C:\\Users\\...\\WeChat Files\\wxid_xxx" (auto-filled)

================================================================================
USAGE
================================================================================

Method 1: Auto Export (Recommended)
----------------------------------
Open CMD, navigate to Wxcrawl folder, run:
    scripts\auto_export.bat

The tool will automatically:
1. Get fresh key from WeChat
2. Decrypt databases
3. Export messages

Method 2: Step by Step
-----------------------
Step 1: Get key
    python scripts\get_key.py

Step 2: Decrypt databases
    python scripts\decrypt_db.py

Step 3: Export messages
    python scripts\export_messages.py

================================================================================
FILE STRUCTURE
================================================================================

Wxcrawl/
├── README.txt              [This file]
├── .gitignore             [Git ignore rules]
├── config.example.json    [Empty template]
└── scripts/
    ├── get_key.py        [Get key from WeChat]
    ├── decrypt_db.py     [Decrypt databases]
    ├── export_messages.py [Export messages]
    └── auto_export.bat   [Run all automatically]

After export:
    export/
    ├── decrypted/              [Decrypted databases]
    └── messages/
        ├── individual_YYYYMMDD_HHMMSS/
        │   ├── ContactName_wxid123.json    [Personal chat]
        │   └── GroupName_xxx@chatroom.json [Group chat]
        └── summary_YYYYMMDD_HHMMSS.json  [Summary]

================================================================================
EXPORT FORMAT
================================================================================

Each conversation exports to one JSON file:
- Filename: Name_wxid.json
- Encoding: UTF-8

Message structure:
{
  "conversation_id": "wxid_xxx or xxx@chatroom",
  "conversation_name": "Display Name",
  "is_chatroom": true/false,
  "type": "Personal" or "Group",
  "total_messages": 100,
  "messages": [
    {
      "msg_id": "123",
      "talker_id": "wxid_xxx",
      "talker_name": "Group Name",
      "is_chatroom": true,
      "sender_id": "wxid_yyy",
      "sender_name": "John Doe",          <-- Sender name (in group)
      "msg_type": 1,
      "content": "Message content",
      "content_preview": "Message...",
      "create_time": 1713456789,
      "datetime": "2024-04-18 20:30:00",
      "is_from_me": true/false,
      "media": {
        "type": "image",
        "md5": "abc123...",
        "width": 800,
        "height": 600
      }
    }
  ]
}

================================================================================
KEY FEATURES
================================================================================

1. Individual File per Conversation
   - Each chat exported to separate JSON file
   - Clean, organized structure

2. Sender Name in Groups
   - Automatically resolves wxid to display name
   - Priority: Remark > NickName > wxid

3. Media Metadata Extraction
   - Extracts MD5, dimensions, CDN URL from XML
   - Actual images require additional decryption

4. Time Conversion
   - Unix timestamp converted to YYYY-MM-DD HH:MM:SS

================================================================================
SCHEDULING (Task Scheduler)
================================================================================

1. Open Task Scheduler (Search "Task Scheduler" in Start Menu)
2. Click "Create Basic Task..."
3. Name: Wxcrawl_Auto_Export
4. Trigger: Daily, Time: 23:00 (or your preferred time)
5. Action: Start a program
   - Program: C:\path\to\Wxcrawl\scripts\auto_export.bat
   - Start in: C:\path\to\Wxcrawl\scripts
6. Conditions: Run whether user is logged on or not
7. Settings: Run with highest privileges
8. Click Finish

================================================================================
TROUBLESHOOTING
================================================================================

1. Error: "WeChat No Run"
   -> Ensure WeChat PC is open and logged in
   -> Try restarting WeChat

2. Error: "Module not found: pywxdump"
   -> Reinstall: pip install pywxdump

3. Error: "Key Error" during decrypt
   -> Key expired, run: python scripts\get_key.py
   -> Restart WeChat PC

4. Cannot export messages
   -> Check config.json has key
   -> Re-run from start: python scripts\get_key.py

5. Vietnamese encoding issues
   -> Ensure files are saved as UTF-8
   -> CMD command: chcp 65001

================================================================================
LIMITATIONS
================================================================================

1. Key Expiration
   - Key expires when WeChat updates or restarts
   - Re-run get_key.py to get new key

2. Platform Support
   - Only WeChat PC (Windows) supported
   - Mac/Linux not supported

3. Media Files
   - Exports metadata only (MD5, dimensions)
   - Actual files require separate decryption

================================================================================
CHANGELOG
================================================================================

v1.0.0 (2026-04-18)
- Export messages per conversation
- Display sender names in groups
- Extract image metadata
- Support WeChat 3.9.x - 4.1.x

================================================================================
SUPPORT
================================================================================

Check log files in the logs/ directory when encountering errors.

================================================================================
