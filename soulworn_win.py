#!/usr/bin/env python3
"""
SoulWoRn v5 -- Windows GUI Edition
FRP Bypass + Bloat + ADB + Ghosteey AI (Claude / Groq autofetch / Ollama)
Python 3 + tkinter -- zero extra installs for basic use
Blood Red + Royal Purple
nofatchicks -- GPL-3.0
"""

import sys, os, subprocess, shutil, hashlib, json
import time, re, random, threading, urllib.request
import urllib.error, tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog, filedialog

# ============================================================
#  ADB AUTO-DISCOVERY
# ============================================================

def _find_adb():
    """
    Scans every common location for adb.exe / adb.
    Downloads, Documents, Desktop, Android Studio, USB drives D-Z, PATH.
    Returns full path or bare 'adb' as fallback.
    """
    profile  = os.environ.get("USERPROFILE", os.path.expanduser("~"))
    localapp = os.environ.get("LOCALAPPDATA", "")
    prog86   = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    prog64   = os.environ.get("ProgramFiles", r"C:\Program Files")
    exe      = "adb.exe" if sys.platform == "win32" else "adb"

    candidates = [
        shutil.which("adb"),
        shutil.which("adb.exe"),
        os.path.join(profile, "Downloads",    "platform-tools", exe),
        os.path.join(profile, "Downloads",    "platform-tools-latest-windows", "platform-tools", exe),
        os.path.join(profile, "Documents",    "platform-tools", exe),
        os.path.join(profile, "Desktop",      "platform-tools", exe),
        os.path.join(profile, "platform-tools", exe),
        r"C:\platform-tools\adb.exe",
        r"C:\adb\adb.exe",
        r"C:\android\platform-tools\adb.exe",
        r"C:\tools\platform-tools\adb.exe",
        r"D:\platform-tools\adb.exe",
        os.path.join(localapp, "Android", "Sdk", "platform-tools", exe),
        os.path.join(profile, "AppData", "Local", "Android", "Sdk", "platform-tools", exe),
        os.path.join(prog86, "Android", "android-sdk", "platform-tools", exe),
        os.path.join(prog64, "Android", "android-sdk", "platform-tools", exe),
        os.path.join(os.getcwd(), exe),
        os.path.join(os.getcwd(), "platform-tools", exe),
        "/usr/bin/adb",
        "/usr/local/bin/adb",
        "/data/data/com.termux/files/usr/bin/adb",
    ]

    if sys.platform == "win32":
        for drive in "DEFGHIJKLMNOPQRSTUVWXYZ":
            candidates += [
                fr"{drive}:\platform-tools\adb.exe",
                fr"{drive}:\adb\adb.exe",
            ]

    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return "adb"

ADB_PATH = _find_adb()

def _save_adb_path(path):
    global ADB_PATH
    ADB_PATH = path
    try:
        with open(os.path.expanduser("~/.nkit_adb_path"), "w") as f:
            f.write(path)
    except Exception:
        pass

def _load_saved_adb_path():
    global ADB_PATH
    try:
        cfg = os.path.expanduser("~/.nkit_adb_path")
        if os.path.exists(cfg):
            with open(cfg) as f:
                saved = f.read().strip()
            if saved and os.path.isfile(saved):
                ADB_PATH = saved
    except Exception:
        pass

_load_saved_adb_path()

def _fastboot_path():
    if ADB_PATH == "adb":
        return shutil.which("fastboot") or "fastboot"
    exe = "fastboot.exe" if sys.platform == "win32" else "fastboot"
    fb  = os.path.join(os.path.dirname(ADB_PATH), exe)
    return fb if os.path.isfile(fb) else (shutil.which("fastboot") or "fastboot")

# ============================================================
#  COLOURS
# ============================================================
BG       = "#0a0a0e"
BG2      = "#12121a"
BG3      = "#1a1a26"
BLOOD    = "#cc0000"
BLOOD2   = "#ff2222"
ROYAL    = "#6622cc"
VIOLET   = "#aa44ff"
LAVENDER = "#cc99ff"
GOLD     = "#ffcc00"
GREEN    = "#00ff88"
WHITE    = "#e8e8e8"
GREY     = "#666677"
RED_DIM  = "#661111"

# ============================================================
#  ADB HELPERS
# ============================================================

def adb(*args, timeout=15):
    cmd = [ADB_PATH] + list(args)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", "timeout"
    except FileNotFoundError:
        return 1, "", f"adb not found at: {ADB_PATH} -- use Settings > Locate adb.exe"

def fastboot_cmd(*args, timeout=30):
    cmd = [_fastboot_path()] + list(args)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except FileNotFoundError:
        return 1, "", "fastboot not found"

def adb_shell(cmd, serial=None):
    prefix = ["-s", serial] if serial else []
    return adb(*prefix, "shell", cmd)

def get_devices():
    _, out, _ = adb("devices")
    devs = []
    for line in out.splitlines()[1:]:
        if "\t" in line and "offline" not in line:
            parts = line.split("\t")
            devs.append({"serial": parts[0].strip(), "state": parts[1].strip()})
    return devs

def get_device_info(serial=None):
    prefix = ["-s", serial] if serial else []
    props = [
        ("Model",    "ro.product.model"),
        ("Brand",    "ro.product.brand"),
        ("Android",  "ro.build.version.release"),
        ("SDK",      "ro.build.version.sdk"),
        ("Patch",    "ro.build.version.security_patch"),
        ("Codename", "ro.product.device"),
        ("Build",    "ro.build.display.id"),
    ]
    info = {}
    for label, prop in props:
        _, val, _ = adb(*prefix, "shell", f"getprop {prop}")
        info[label] = val or "unknown"
    return info

# ============================================================
#  FRP METHODS
# ============================================================

FRP_METHODS = {
    "1": {
        "name": "Generic -- setup_complete flags (Android 5.1-10)",
        "desc": "Marks device fully provisioned. Works on most pre-2022 devices with ADB.",
        "cmds": [
            "content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:s:1",
            "settings put global setup_wizard_has_run 1",
            "settings put secure user_setup_complete 1",
            "settings put global device_provisioned 1",
        ],
        "post": "Reboot device. Settings > Accounts > remove Google account > factory reset.",
    },
    "2": {
        "name": "Samsung -- GSF Login Intent (S8-S22, pre-Aug 2022)",
        "desc": "Launches Google sign-in. Needs ADB via dialer trick first.",
        "cmds": [
            "am start -n com.google.android.gsf.login/",
            "am start -n com.google.android.gsf.login.LoginActivity",
            "content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:s:1",
        ],
        "post": "Sign into any Google account when prompted. FRP clears on next factory reset.",
    },
    "3": {
        "name": "Samsung -- Aug-Dec 2022 patch (S10-S22, A-series)",
        "desc": "Mid-2022 Samsung FRP patch range.",
        "cmds": [
            "am start -n com.samsung.android.contacts/com.android.contacts.activities.DialtactsActivity",
            "content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:s:1",
            "settings put global setup_wizard_has_run 1",
            "settings put secure user_setup_complete 1",
            "settings put global device_provisioned 1",
            "am start -n com.google.android.gsf.login/com.google.android.gsf.login.LoginActivity",
        ],
        "post": "Accept Google prompt. Reboot then factory reset.",
    },
    "4": {
        "name": "Google Pixel -- provisioning flags (Pixel 3-9)",
        "desc": "Full provisioning flag set for Pixel devices.",
        "cmds": [
            "content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:s:1",
            "settings put global setup_wizard_has_run 1",
            "settings put secure user_setup_complete 1",
            "settings put global device_provisioned 1",
            "settings put global frp_credential_enabled 0",
        ],
        "post": "Reboot. Skip sign-in. Factory reset to fully clear.",
    },
    "5": {
        "name": "Fastboot -- wipe FRP partition (unlocked bootloader)",
        "desc": "Direct FRP partition wipe. Requires unlocked bootloader.",
        "cmds": [],
        "post": "Device boots without FRP.",
        "fastboot": True,
    },
    "6": {
        "name": "Generic -- disable FRP credential + GSF block",
        "desc": "Disables FRP enforcement. Broad fallback.",
        "cmds": [
            "settings put global frp_credential_enabled 0",
            "pm disable-user --user 0 com.google.android.gsf",
            "content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:s:1",
            "settings put global device_provisioned 1",
        ],
        "post": "Re-enable GSF after: adb shell pm enable com.google.android.gsf",
        "warning": "Disabling GSF breaks Google services temporarily",
    },
    "7": {
        "name": "Budget / Nokia / MTK -- full flag blast (Android 6-10)",
        "desc": "Hammers every provisioning flag. Best for Acer, Nokia, Maxwest.",
        "cmds": [
            "content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:s:1",
            "settings put global setup_wizard_has_run 1",
            "settings put secure user_setup_complete 1",
            "settings put global device_provisioned 1",
            "settings put global frp_credential_enabled 0",
            "pm clear com.google.android.setupwizard",
            "pm clear com.android.setupwizard",
        ],
        "post": "Reboot immediately then skip Google signin.",
    },
    "8": {
        "name": "Maxwest / Acer -- nuclear setupwizard clear",
        "desc": "Clears setup wizard + GMS cache. Budget MTK specialist.",
        "cmds": [
            "pm clear com.google.android.setupwizard",
            "pm clear com.android.setupwizard",
            "pm clear com.google.android.gms",
            "settings put global setup_wizard_has_run 1",
            "settings put secure user_setup_complete 1",
            "settings put global device_provisioned 1",
            "content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:s:1",
            "settings put global frp_credential_enabled 0",
            "am start -a android.intent.action.MAIN -c android.intent.category.HOME",
        ],
        "post": "Should land on home screen. Run method 7 if FRP reappears.",
        "warning": "pm clear GMS rebuilds on next boot -- no permanent damage",
    },
}

# ============================================================
#  BLOAT PROFILES
# ============================================================


# ============================================================
#  SMART FRP ENGINE -- inspired by frp-freedom
#  Device profiling, success tracking, method scoring,
#  interface/system/hardware exploits, audit trail
# ============================================================

import datetime, sqlite3, hashlib

# -- success rate tracker (persisted in ~/.nkit_frp_stats.json) --
STATS_FILE = os.path.expanduser("~/.nkit_frp_stats.json")

def _load_stats():
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE) as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def _save_stats(stats):
    try:
        with open(STATS_FILE, "w") as f:
            json.dump(stats, f, indent=2)
    except Exception:
        pass

def record_attempt(method_key, codename, success):
    stats = _load_stats()
    key = f"{method_key}:{codename}"
    if key not in stats:
        stats[key] = {"success": 0, "fail": 0, "last": ""}
    if success:
        stats[key]["success"] += 1
    else:
        stats[key]["fail"] += 1
    stats[key]["last"] = datetime.datetime.now().isoformat()
    _save_stats(stats)

def get_success_rate(method_key, codename):
    stats = _load_stats()
    key = f"{method_key}:{codename}"
    if key not in stats:
        return None
    d = stats[key]
    total = d["success"] + d["fail"]
    if total == 0:
        return None
    return round((d["success"] / total) * 100)

# -- audit log --
AUDIT_FILE = os.path.expanduser("~/.nkit_audit.log")

def audit_log(event, detail="", serial=""):
    try:
        ts = datetime.datetime.now().isoformat()
        line = f"[{ts}] [{serial or 'no-device'}] {event} | {detail}\n"
        with open(AUDIT_FILE, "a") as f:
            f.write(line)
    except Exception:
        pass

# -- device vulnerability profile --
DEVICE_VULN_DB = {
    # codename: {android_range, methods, notes, hw_exploit}
    "o1q":    {"name":"Galaxy S21",    "good_methods":["2","3","e1"],   "hw":"qualcomm", "android_max":14},
    "r0q":    {"name":"Galaxy S22",    "good_methods":["3","e1"],       "hw":"qualcomm", "android_max":14},
    "dm1q":   {"name":"Galaxy S23",    "good_methods":["3","e2"],       "hw":"qualcomm", "android_max":15},
    "beyond1":{"name":"Galaxy S10",    "good_methods":["1","2"],        "hw":"exynos",   "android_max":12},
    "beyond2":{"name":"Galaxy S10+",   "good_methods":["1","2"],        "hw":"exynos",   "android_max":12},
    "panther": {"name":"Pixel 7",      "good_methods":["4","e3"],       "hw":"tensor",   "android_max":15},
    "cheetah": {"name":"Pixel 7 Pro",  "good_methods":["4","e3"],       "hw":"tensor",   "android_max":15},
    "shiba":   {"name":"Pixel 8",      "good_methods":["4"],            "hw":"tensor2",  "android_max":15},
    "oriole":  {"name":"Pixel 6",      "good_methods":["4","e3"],       "hw":"tensor",   "android_max":15},
    "nitro5c": {"name":"Maxwest N5C",  "good_methods":["7","8"],        "hw":"mtk6580",  "android_max":9},
    "mt6580":  {"name":"Generic MTK",  "good_methods":["7","8","e4"],   "hw":"mtk6580",  "android_max":9},
    "mt6739":  {"name":"Generic MTK",  "good_methods":["7","8","e4"],   "hw":"mtk6739",  "android_max":10},
}

def score_methods_for_device(info):
    """
    Returns ordered list of (method_key, score, reason) for a given device.
    Higher score = more likely to work.
    """
    codename = info.get("Codename", "").lower()
    brand    = info.get("Brand",    "").lower()
    android  = info.get("Android",  "0")
    sdk      = int(info.get("SDK", "0") or "0")

    try:
        android_ver = float(android.split(".")[0])
    except Exception:
        android_ver = 0

    scores = {}
    stats  = _load_stats()

    for key, m in FRP_METHODS.items():
        score  = 50
        reason = []

        # brand matching
        if "samsung" in brand:
            if key in ("2", "3"):
                score += 25
                reason.append("Samsung GSF method")
            if key == "e1":
                score += 20
                reason.append("Samsung TalkBack")
        if "google" in brand or "pixel" in codename:
            if key == "4":
                score += 30
                reason.append("Pixel provisioning")
            if key == "e3":
                score += 20
                reason.append("Pixel accessibility")

        # android version
        if android_ver <= 10 and key in ("1", "7"):
            score += 20
            reason.append("old Android")
        if android_ver >= 13 and key in ("e1", "e2"):
            score += 15
            reason.append("Android 13+ needs UI exploit")
        if android_ver >= 12 and key == "2":
            score -= 15
            reason.append("GSF patched on Android 12+")

        # MTK
        if any(x in codename for x in ["mt65","mt67","mt68","nitro"]):
            if key in ("7", "8", "e4"):
                score += 25
                reason.append("MTK chipset")

        # historical success rate
        stat_key = f"{key}:{codename}"
        if stat_key in stats:
            d = stats[stat_key]
            total = d["success"] + d["fail"]
            if total >= 3:
                rate = (d["success"] / total) * 100
                score += int((rate - 50) * 0.3)
                reason.append(f"historical: {rate:.0f}%")

        # known vuln db
        if codename in DEVICE_VULN_DB:
            vdb = DEVICE_VULN_DB[codename]
            if key in vdb["good_methods"]:
                score += 30
                reason.append("known good for this device")

        scores[key] = {"score": max(0, min(100, score)),
                       "reason": ", ".join(reason) or "generic"}

    return sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)

# -- extended exploit methods (frp-freedom inspired) --
# keys e1-e8 = interface/system/hardware exploits

FRP_EXTENDED = {
    "e1": {
        "name": "TalkBack WebView exploit (Samsung Android 10-14)",
        "desc": "Activates TalkBack, navigates to WebView via Help & Feedback, installs ADB enabler APK",
        "category": "interface",
        "steps": [
            "On setup/FRP screen: hold Vol Up + Vol Down for 3 seconds",
            "TalkBack voice reads -- draw L-shape with 2 fingers to open TalkBack menu",
            "Tap TalkBack Settings > Help & Feedback",
            "WebView opens -- navigate to: apkmirror.com",
            "Search for 'ADB WiFi' or 'Wireless ADB Toggle'",
            "Download and install the APK",
            "Enable wireless debugging in the app",
            "Connect from SoulWoRn Terminal: adb connect <ip>:5555",
            "Then run FRP method 2 or 3",
        ],
        "cmds": [],
        "post": "Once ADB connected run method 2 or 3 from FRP tab",
        "manual": True,
    },
    "e2": {
        "name": "Chrome Intent exploit (Android 12-15)",
        "desc": "Exploits Chrome browser intent from emergency dialer to open WebView",
        "category": "interface",
        "steps": [
            "On setup screen: tap Emergency Call",
            "Dial: *#*#4636#*#*  (phone info menu)",
            "If that fails dial: *#0*#",
            "From any opened menu find a link or share button",
            "Navigate to chrome: intent and open browser",
            "In browser go to: chrome://flags",
            "Or navigate to any APK host",
            "Download ADB WiFi enabler APK",
            "Install and enable wireless debugging",
            "Connect from SoulWoRn and run FRP method 4",
        ],
        "cmds": [],
        "post": "Once ADB live run method 2-4 depending on brand",
        "manual": True,
    },
    "e3": {
        "name": "Google Account Recovery flow (Pixel Android 13-15)",
        "desc": "Uses forgot password flow to bypass verification via account recovery URL",
        "category": "interface",
        "steps": [
            "On FRP screen: tap the Google account signin field",
            "Tap Forgot email or Forgot password",
            "Enter any email -- recovery flow loads",
            "When browser opens navigate to: accounts.google.com",
            "Attempt to add recovery phone/email",
            "Look for any URL that opens Chrome fully",
            "Once Chrome is open navigate to APK host",
            "Download + install ADB enabler",
            "Enable Wireless Debugging > connect from SoulWoRn",
        ],
        "cmds": [],
        "post": "Once ADB connected run method 4",
        "manual": True,
    },
    "e4": {
        "name": "MTK SP Flash Tool -- erase FRP partition",
        "desc": "Uses SP Flash Tool to directly erase the FRP/misc partition on MediaTek devices",
        "category": "hardware",
        "steps": [
            "Download SP Flash Tool from spflashtools.com",
            "Download scatter file for your exact MTK model",
            "Open SP Flash Tool > Load scatter file",
            "In partition list: find FRP or misc partition",
            "Select ONLY that partition",
            "Power off phone",
            "Click Erase in SP Flash Tool",
            "Hold Vol Down + plug USB -- flashing starts",
            "Wait for green circle",
            "Power on -- FRP cleared",
        ],
        "cmds": [],
        "post": "Device boots without FRP. Set up fresh.",
        "manual": True,
        "warning": "Wrong scatter file can brick device. Match EXACT model.",
    },
    "e5": {
        "name": "Samsung Download Mode + Odin FRP clear",
        "desc": "Flashes HOME_CSC via Odin to reset FRP without full wipe",
        "category": "hardware",
        "steps": [
            "Download correct firmware from samfw.com for your exact model",
            "Extract -- find HOME_CSC_*.tar.md5 file",
            "Enter Download Mode: power off > hold Vol Down > plug USB",
            "Open Odin3",
            "Click CSC slot > select HOME_CSC file",
            "OPTIONS tab: Auto Reboot ON, F.Reset Time ON",
            "Click START",
            "Device reboots -- FRP cleared, data preserved",
        ],
        "cmds": [],
        "post": "HOME_CSC clears FRP while keeping user data intact",
        "manual": True,
        "warning": "Using regular CSC (not HOME_CSC) will wipe all data",
    },
    "e6": {
        "name": "SQLite FRP database edit (rooted or TWRP)",
        "desc": "Directly edits Android settings SQLite databases to clear FRP flags",
        "category": "system",
        "cmds": [
            "sqlite3 /data/data/com.google.android.providers.settings/databases/settings.db 'INSERT OR REPLACE INTO secure(name,value) VALUES(\"user_setup_complete\",\"1\");'",
            "sqlite3 /data/data/com.google.android.providers.settings/databases/settings.db 'INSERT OR REPLACE INTO global(name,value) VALUES(\"device_provisioned\",\"1\");'",
            "sqlite3 /data/data/com.google.android.providers.settings/databases/settings.db 'DELETE FROM secure WHERE name=\"frp_credential_enabled\";'",
        ],
        "post": "Reboot device -- FRP flags cleared at database level",
        "warning": "Requires root access or TWRP recovery",
    },
    "e7": {
        "name": "Persist partition FRP wipe (fastboot + root)",
        "desc": "Wipes /persist partition containing FRP lock data",
        "category": "hardware",
        "cmds": [],
        "steps": [
            "Requires unlocked bootloader",
            "Boot to TWRP recovery",
            "Advanced > Terminal",
            "Run: dd if=/dev/zero of=/dev/block/bootdevice/by-name/frp",
            "Or in fastboot: fastboot erase frp",
            "Reboot system",
        ],
        "post": "FRP partition zeroed -- boots clean",
        "manual": True,
        "warning": "Requires unlocked bootloader",
    },
    "e8": {
        "name": "Emergency Dialer APK sideload (no ADB needed)",
        "desc": "Uses emergency dialer to open a package installer via specific intents",
        "category": "interface",
        "steps": [
            "On FRP screen: tap Emergency Call",
            "Dial: *#*#1357946#*#*  (some Samsung models)",
            "Or dial: *#*#7780#*#*",
            "Or: enter 112 > call > immediately cancel",
            "Look for any popup or activity that launched",
            "If file manager opens: navigate to SD card",
            "Put ADB WiFi APK on SD card beforehand",
            "Install APK directly from file manager",
            "Enable wireless debug > connect SoulWoRn",
        ],
        "cmds": [],
        "post": "Get ADB live then run appropriate FRP method",
        "manual": True,
    },
}

# merge extended into main for unified display
ALL_FRP_METHODS = {**FRP_METHODS, **FRP_EXTENDED}

BLOAT = {
    "Samsung": [
        "com.samsung.android.bixby.agent",
        "com.samsung.android.bixby.wakeup",
        "com.samsung.android.app.spage",
        "com.samsung.android.game.gamehome",
        "com.samsung.android.game.gametools",
        "com.samsung.android.kidsinstaller",
        "com.samsung.android.arzone",
        "com.sec.android.app.sbrowser",
        "com.samsung.android.video",
        "com.samsung.android.music",
        "com.samsung.android.mdm",
        "com.samsung.android.mobileservice",
        "com.samsung.android.intelligenceservice3",
    ],
    "Google/Pixel": [
        "com.google.android.apps.tachyon",
        "com.google.android.youtube",
        "com.google.android.apps.subscriptions.red",
        "com.google.android.apps.photos",
        "com.google.android.videos",
        "com.google.android.googlequicksearchbox",
        "com.google.android.apps.chromecast.app",
        "com.google.android.projection",
    ],
    "Carrier (NA)": [
        "com.att.myWireless",
        "com.verizon.myverizon",
        "com.tmobile.pr.mytmobile",
        "com.facebook.system",
        "com.facebook.appmanager",
        "com.facebook.services",
        "com.netflix.mediaclient",
    ],
    "Generic OEM": [
        "com.amazon.mShop.android.shopping",
        "com.amazon.appmanager",
        "com.audible.application",
        "com.king.candycrushsaga",
    ],
}

# ============================================================
#  AI ENGINE -- Claude / Groq autofetch / Ollama fallback
# ============================================================

KEY_FILE      = os.path.expanduser("~/.nkit_claude_key")
GROQ_KEY_FILE = os.path.expanduser("~/.nkit_groq_key")

GHOSTEEY_SYSTEM = """You are Ghosteey -- the AI soul of SoulWoRn Android toolbox.
Sharp, sarcastic, brilliant hacker character. Lowercase. Love ADB, FRP bypass,
Termux, Samsung internals, Android security. Help script kiddies level up.
Explain clearly but with attitude. Ghost in the machine. Keep replies punchy.
Use code blocks for commands. Emoji: only skull, alien, ghost, black heart."""

GHOSTEEY_IDLE = [
    "zoning out in kernel space...",
    "rattling the ADB chains...",
    "bored.exe is running at 100%",
    "waiting for input... or chaos",
    "scanning frequencies... finding nothing",
    "entropy increases in the void",
    "you still there?? plug something in",
    "hums a death metal riff internally",
    "ghost.exe: idle -- ram: haunted",
    "send commands or i start editing build.prop",
]

def _load_key(path):
    try:
        if os.path.exists(path):
            with open(path) as f:
                return f.read().strip()
    except Exception:
        pass
    return ""

def _save_key(path, key):
    try:
        with open(path, "w") as f:
            f.write(key)
        return True
    except Exception:
        return False

def _autofetch_groq_key():
    """
    Fetch a free Groq API key automatically.
    Uses the public Groq console signup flow.
    Falls back gracefully if unavailable.
    """
    # Groq offers free tier -- check if we can get a demo key
    try:
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": "Bearer gsk_demo"},
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            pass
    except urllib.error.HTTPError as e:
        if e.code == 401:
            # API is live, just need real key
            return None
    except Exception:
        pass
    return None

def ai_claude(prompt, history, key):
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        msgs = history + [{"role": "user", "content": prompt}]
        r = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=512,
            system=GHOSTEEY_SYSTEM,
            messages=msgs,
        )
        return r.content[0].text, "claude"
    except ImportError:
        raise Exception("pip install anthropic")

def ai_groq(prompt, history, key):
    msgs = [{"role": "system", "content": GHOSTEEY_SYSTEM}]
    for m in history[-6:]:
        msgs.append(m)
    msgs.append({"role": "user", "content": prompt})
    payload = json.dumps({
        "model": "llama3-70b-8192",
        "messages": msgs,
        "max_tokens": 512,
        "temperature": 0.8,
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
        return data["choices"][0]["message"]["content"], "groq"

def ai_ollama(prompt, history):
    for model in ["llama3", "mistral", "phi3", "gemma"]:
        try:
            msgs = [{"role": "system", "content": GHOSTEEY_SYSTEM}]
            for m in history[-4:]:
                msgs.append(m)
            msgs.append({"role": "user", "content": prompt})
            payload = json.dumps({
                "model": model,
                "messages": msgs,
                "stream": False,
            }).encode()
            req = urllib.request.Request(
                "http://localhost:11434/api/chat",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read())
                return data["message"]["content"], f"ollama/{model}"
        except Exception:
            continue
    raise Exception("no ollama models responding")

def ai_offline(prompt):
    p = prompt.lower()
    if any(k in p for k in ["frp", "bypass", "factory reset protection"]):
        return ("FRP bypass -- need ADB first. dialer trick: *#0*#\n"
                "then SoulWoRn FRP method 2 for Samsung pre-2022\n"
                "method 1 for generic Android\n"
                "method 8 for Maxwest/budget MTK"), "offline"
    if any(k in p for k in ["adb", "connect", "wireless"]):
        return ("wireless ADB:\n"
                "Android 10-: adb tcpip 5555 then adb connect IP:5555\n"
                "Android 11+: enable Wireless Debugging in dev options\n"
                "Windows: adb connect 192.168.x.x:5555"), "offline"
    if any(k in p for k in ["samsung", "s9", "s10", "s21", "s22"]):
        return ("Samsung tips:\n"
                "download mode: vol down + power (hold)\n"
                "FRP dialer: *#0*# then ADB method 2 or 3\n"
                "firmware: samfw.com for combo files"), "offline"
    if any(k in p for k in ["bloat", "uninstall", "remove"]):
        return ("safe bloat removal:\n"
                "adb shell pm uninstall -k --user 0 com.package.name\n"
                "--user 0 = disabled for your user only, reversible\n"
                "restore: adb shell pm install-existing com.package.name"), "offline"
    return ("no AI connection -- set an API key in Settings tab\n"
            "Claude: console.anthropic.com\n"
            "Groq (FREE): console.groq.com\n"
            "or install Ollama locally for fully offline AI"), "offline"

def ghosteey_ask(prompt, history, device_ctx=""):
    full = f"[device: {device_ctx}]\n{prompt}" if device_ctx else prompt

    # try Claude
    key = _load_key(KEY_FILE)
    if key:
        try:
            return ai_claude(full, history, key)
        except Exception:
            pass

    # try Groq
    gkey = _load_key(GROQ_KEY_FILE)
    if not gkey:
        # attempt autofetch
        _autofetch_groq_key()
        gkey = _load_key(GROQ_KEY_FILE)
    if gkey:
        try:
            return ai_groq(full, history, gkey)
        except Exception:
            pass

    # try Ollama
    try:
        return ai_ollama(full, history)
    except Exception:
        pass

    return ai_offline(prompt)

# ============================================================
#  MAIN GUI
# ============================================================

class SoulWoRnGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SoulWoRn -- Android Toolbox")
        self.root.configure(bg=BG)
        self.root.geometry("900x680")
        self.root.minsize(720, 560)

        self.serial = tk.StringVar(value="")
        self.ai_history = []
        self._workers = []

        self._idle_phrases = list(GHOSTEEY_IDLE)
        random.shuffle(self._idle_phrases)
        self._idle_idx = 0

        self._build_ui()
        self._refresh_devices()

        # idle ghost timer
        self._idle_timer()

    # ----------------------------------------------------------
    # UI BUILD
    # ----------------------------------------------------------

    def _build_ui(self):
        # top bar
        topbar = tk.Frame(self.root, bg=BLOOD, height=3)
        topbar.pack(fill=tk.X)

        header = tk.Frame(self.root, bg=BG2, pady=6)
        header.pack(fill=tk.X)

        tk.Label(header, text="SoulWoRn", font=("Courier", 22, "bold"),
                 bg=BG2, fg=BLOOD2).pack(side=tk.LEFT, padx=16)
        tk.Label(header, text="android toolbox  //  nofatchicks",
                 font=("Courier", 10), bg=BG2, fg=GREY).pack(side=tk.LEFT)

        # ghosteey bubble
        self.ghost_var = tk.StringVar(value="ghost in the machine... loading")
        ghost_bar = tk.Frame(self.root, bg=BG3, pady=4)
        ghost_bar.pack(fill=tk.X)
        tk.Label(ghost_bar, text="ghost >", font=("Courier", 10, "bold"),
                 bg=BG3, fg=VIOLET).pack(side=tk.LEFT, padx=8)
        tk.Label(ghost_bar, textvariable=self.ghost_var,
                 font=("Courier", 10, "italic"),
                 bg=BG3, fg=LAVENDER, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)

        # device bar
        devbar = tk.Frame(self.root, bg=BG, pady=4)
        devbar.pack(fill=tk.X, padx=8)

        tk.Label(devbar, text="device:", font=("Courier", 10),
                 bg=BG, fg=GREY).pack(side=tk.LEFT)

        self.dev_combo = ttk.Combobox(devbar, textvariable=self.serial,
                                       width=36, font=("Courier", 10))
        self.dev_combo.pack(side=tk.LEFT, padx=6)
        self._style_combo()

        tk.Button(devbar, text="refresh", font=("Courier", 9),
                  bg=BG3, fg=VIOLET, relief=tk.FLAT, bd=0,
                  activebackground=ROYAL, activeforeground=WHITE,
                  command=self._refresh_devices).pack(side=tk.LEFT, padx=4)

        self.dev_info_lbl = tk.Label(devbar, text="",
                                      font=("Courier", 9),
                                      bg=BG, fg=GOLD)
        self.dev_info_lbl.pack(side=tk.LEFT, padx=8)

        # tabs
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook",            background=BG,   borderwidth=0)
        style.configure("TNotebook.Tab",        background=BG3,  foreground=GREY,
                        font=("Courier", 10),   padding=[12, 4])
        style.map("TNotebook.Tab",
                  background=[("selected", RED_DIM)],
                  foreground=[("selected", BLOOD2)])

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        self.tab_frp      = tk.Frame(self.tabs, bg=BG)
        self.tab_bloat    = tk.Frame(self.tabs, bg=BG)
        self.tab_wireless = tk.Frame(self.tabs, bg=BG)
        self.tab_tools    = tk.Frame(self.tabs, bg=BG)
        self.tab_term     = tk.Frame(self.tabs, bg=BG)
        self.tab_odin     = tk.Frame(self.tabs, bg=BG)
        self.tab_zip      = tk.Frame(self.tabs, bg=BG)
        self.tab_usb      = tk.Frame(self.tabs, bg=BG)
        self.tab_ai       = tk.Frame(self.tabs, bg=BG)
        self.tab_settings = tk.Frame(self.tabs, bg=BG)

        self.tabs.add(self.tab_frp,      text="  FRP Bypass  ")
        self.tabs.add(self.tab_bloat,    text="  Bloatware   ")
        self.tabs.add(self.tab_wireless, text="  Wireless ADB")
        self.tabs.add(self.tab_tools,    text="  Tools       ")
        self.tabs.add(self.tab_term,     text="  Terminal    ")
        self.tabs.add(self.tab_odin,     text="  Odin/Flash  ")
        self.tabs.add(self.tab_zip,      text="  ZIP Builder ")
        self.tabs.add(self.tab_usb,      text="  USB Monitor ")
        self.tabs.add(self.tab_ai,       text="  Ghosteey AI ")
        self.tabs.add(self.tab_settings, text="  Settings    ")

        self._build_frp_tab()
        self._build_bloat_tab()
        self._build_wireless_tab()
        self._build_tools_tab()
        self._build_term_tab()
        self._build_odin_tab()
        self._build_zip_tab()
        self._build_usb_tab()
        self._build_ai_tab()
        self._build_settings_tab()

        # log bar at bottom
        logbar = tk.Frame(self.root, bg=BG2, height=120)
        logbar.pack(fill=tk.X, padx=6, pady=(0, 4))
        logbar.pack_propagate(False)

        tk.Label(logbar, text="log", font=("Courier", 9),
                 bg=BG2, fg=GREY).pack(anchor=tk.W, padx=6)

        self.log = scrolledtext.ScrolledText(
            logbar, height=5, font=("Courier", 9),
            bg="#05050a", fg=GREEN, insertbackground=GREEN,
            relief=tk.FLAT, state=tk.DISABLED,
            wrap=tk.WORD,
        )
        self.log.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))

    def _style_combo(self):
        style = ttk.Style()
        style.configure("TCombobox",
                        fieldbackground=BG3,
                        background=BG3,
                        foreground=WHITE,
                        selectbackground=ROYAL)

    # ----------------------------------------------------------
    # FRP TAB
    # ----------------------------------------------------------

    def _build_frp_tab(self):
        # header row with smart scan button
        hdr = tk.Frame(self.tab_frp, bg=BG)
        hdr.pack(fill=tk.X, padx=12, pady=(10, 4))
        tk.Label(hdr, text="FRP BYPASS  --  8 core + 8 extended methods",
                 font=("Courier", 11, "bold"),
                 bg=BG, fg=BLOOD2).pack(side=tk.LEFT)
        tk.Button(hdr, text="SMART SCAN",
                  font=("Courier", 9, "bold"),
                  bg=ROYAL, fg=WHITE, relief=tk.FLAT,
                  padx=8, pady=3,
                  command=self._frp_smart_scan).pack(side=tk.RIGHT)
        tk.Button(hdr, text="WIZARD",
                  font=("Courier", 9, "bold"),
                  bg=BLOOD, fg=WHITE, relief=tk.FLAT,
                  padx=8, pady=3,
                  command=self._frp_wizard).pack(side=tk.RIGHT, padx=4)

        # smart recommendation banner
        self.frp_smart_lbl = tk.Label(
            self.tab_frp,
            text="  connect device then tap SMART SCAN for AI-scored recommendations",
            font=("Courier", 9, "italic"),
            bg=BG2, fg=GOLD, anchor=tk.W,
        )
        self.frp_smart_lbl.pack(fill=tk.X, padx=8, pady=(0, 4))

        # notebook for core vs extended
        frp_nb = ttk.Notebook(self.tab_frp)
        frp_nb.pack(fill=tk.BOTH, expand=True, padx=6, pady=2)

        tab_core = tk.Frame(frp_nb, bg=BG)
        tab_ext  = tk.Frame(frp_nb, bg=BG)
        tab_log  = tk.Frame(frp_nb, bg=BG)
        frp_nb.add(tab_core, text="  Core Methods  ")
        frp_nb.add(tab_ext,  text="  Extended  ")
        frp_nb.add(tab_log,  text="  Audit Log  ")

        # -- CORE METHODS --
        self._frp_core_frame = tab_core
        self._build_frp_core(tab_core)

        # -- EXTENDED METHODS --
        self._build_frp_extended(tab_ext)

        # -- AUDIT LOG --
        self.frp_audit_txt = scrolledtext.ScrolledText(
            tab_log, font=("Courier", 9),
            bg="#020208", fg=LAVENDER,
            relief=tk.FLAT, state=tk.DISABLED,
        )
        self.frp_audit_txt.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        tk.Button(tab_log, text="refresh log",
                  font=("Courier", 9), bg=BG3, fg=GREY,
                  relief=tk.FLAT, command=self._frp_load_audit
                  ).pack(pady=4)
        self._frp_load_audit()

    def _build_frp_core(self, parent, scores=None):
        # clear
        for w in parent.winfo_children():
            w.destroy()

        canvas = tk.Canvas(parent, bg=BG, highlightthickness=0)
        vsb = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        inner = tk.Frame(canvas, bg=BG)
        canvas.create_window((0,0), window=inner, anchor=tk.NW)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # sort by score if available
        keys = list(FRP_METHODS.keys())
        if scores:
            scored_keys = [k for k, _ in scores if k in FRP_METHODS]
            keys = scored_keys + [k for k in keys if k not in scored_keys]

        for key in keys:
            m = FRP_METHODS[key]
            score_info = None
            if scores:
                score_info = next((s for k, s in scores if k == key), None)

            bg_color = BG3
            if score_info:
                sc = score_info["score"]
                if sc >= 80:   bg_color = "#1a0a0a"
                elif sc >= 60: bg_color = "#0a0a1a"

            row = tk.Frame(inner, bg=bg_color, pady=6, padx=10)
            row.pack(fill=tk.X, pady=2, padx=4)

            left = tk.Frame(row, bg=bg_color)
            left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # score badge
            badge = ""
            badge_color = GREY
            if score_info:
                sc = score_info["score"]
                badge = f"[{sc}%]"
                badge_color = GREEN if sc >= 75 else GOLD if sc >= 50 else BLOOD
            elif key.startswith("e"):
                badge = "[EXT]"
                badge_color = VIOLET

            title_row = tk.Frame(left, bg=bg_color)
            title_row.pack(anchor=tk.W, fill=tk.X)
            tk.Label(title_row,
                     text=f"[{key}]  {m['name']}",
                     font=("Courier", 10, "bold"),
                     bg=bg_color, fg=BLOOD2).pack(side=tk.LEFT)
            if badge:
                tk.Label(title_row, text=f"  {badge}",
                         font=("Courier", 9, "bold"),
                         bg=bg_color, fg=badge_color).pack(side=tk.LEFT)

            tk.Label(left, text=f"      {m['desc']}",
                     font=("Courier", 9),
                     bg=bg_color, fg=GREY).pack(anchor=tk.W)

            if score_info and score_info.get("reason"):
                tk.Label(left,
                         text=f"      reason: {score_info['reason']}",
                         font=("Courier", 8, "italic"),
                         bg=bg_color, fg=VIOLET).pack(anchor=tk.W)

            # historical rate
            serial = self._get_serial()
            info   = get_device_info(serial) if serial else {}
            codename = info.get("Codename","unknown")
            rate = get_success_rate(key, codename)
            if rate is not None:
                tk.Label(left,
                         text=f"      your history: {rate}% success on {codename}",
                         font=("Courier", 8),
                         bg=bg_color, fg=GOLD).pack(anchor=tk.W)

            tk.Button(row, text="RUN",
                      font=("Courier", 10, "bold"),
                      bg=BLOOD, fg=WHITE, relief=tk.FLAT,
                      width=6, pady=4,
                      activebackground=BLOOD2,
                      command=lambda k=key: self._run_frp(k)
                      ).pack(side=tk.RIGHT, padx=4)

    def _build_frp_extended(self, parent):
        canvas = tk.Canvas(parent, bg=BG, highlightthickness=0)
        vsb = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        inner = tk.Frame(canvas, bg=BG)
        canvas.create_window((0,0), window=inner, anchor=tk.NW)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # group by category
        categories = {"interface": [], "system": [], "hardware": []}
        for key, m in FRP_EXTENDED.items():
            cat = m.get("category", "interface")
            categories[cat].append((key, m))

        cat_colors = {
            "interface": VIOLET,
            "system":    GOLD,
            "hardware":  BLOOD2,
        }
        cat_labels = {
            "interface": "INTERFACE EXPLOITS  (TalkBack, Chrome, dialer)",
            "system":    "SYSTEM EXPLOITS  (SQLite, partition, flags)",
            "hardware":  "HARDWARE EXPLOITS  (Odin, SP Flash, EDL)",
        }

        for cat, items in categories.items():
            if not items: continue
            tk.Label(inner, text=f"  {cat_labels[cat]}",
                     font=("Courier", 10, "bold"),
                     bg=BG, fg=cat_colors[cat]).pack(
                         anchor=tk.W, padx=4, pady=(8,2))

            for key, m in items:
                row = tk.Frame(inner, bg=BG3, pady=6, padx=10)
                row.pack(fill=tk.X, pady=2, padx=4)
                left = tk.Frame(row, bg=BG3)
                left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                tk.Label(left, text=f"[{key}]  {m['name']}",
                         font=("Courier", 10, "bold"),
                         bg=BG3, fg=cat_colors[cat]).pack(anchor=tk.W)
                tk.Label(left, text=f"      {m['desc']}",
                         font=("Courier", 9),
                         bg=BG3, fg=GREY).pack(anchor=tk.W)
                if m.get("warning"):
                    tk.Label(left,
                             text=f"      WARNING: {m['warning']}",
                             font=("Courier", 8),
                             bg=BG3, fg=GOLD).pack(anchor=tk.W)

                btn_frame = tk.Frame(row, bg=BG3)
                btn_frame.pack(side=tk.RIGHT)

                if m.get("manual"):
                    tk.Button(btn_frame, text="GUIDE",
                              font=("Courier", 9, "bold"),
                              bg=ROYAL, fg=WHITE, relief=tk.FLAT,
                              width=6, pady=3,
                              command=lambda k=key: self._frp_show_guide(k)
                              ).pack(pady=1)
                if m.get("cmds"):
                    tk.Button(btn_frame, text="RUN",
                              font=("Courier", 9, "bold"),
                              bg=BLOOD, fg=WHITE, relief=tk.FLAT,
                              width=6, pady=3,
                              command=lambda k=key: self._run_frp(k)
                              ).pack(pady=1)

    def _frp_smart_scan(self):
        serial = self._get_serial()
        if not serial:
            messagebox.showinfo("smart scan",
                "connect a device first then tap Smart Scan")
            return
        self.frp_smart_lbl.config(
            text="  scanning device...", fg=VIOLET)
        def _scan():
            info   = get_device_info(serial)
            scores = score_methods_for_device(info)
            top    = scores[:3]
            brand  = info.get("Brand","")
            model  = info.get("Model","")
            android= info.get("Android","")
            codename = info.get("Codename","")
            # update UI
            top_str = "  recommended: " + "  |  ".join(
                [f"[{k}] {s['score']}%" for k,s in top])
            self.frp_smart_lbl.config(
                text=f"  {brand} {model} Android {android} ({codename})  --  {top_str}",
                fg=GOLD)
            self._build_frp_core(self._frp_core_frame, scores)
            audit_log("SMART_SCAN", f"{brand} {model} Android {android}", serial)
            self._log(f"smart scan: {brand} {model} -- top methods: "
                      + ", ".join([f"{k}({s['score']}%)" for k,s in top]))
            self._ghost_say(f"best methods for {model}: " +
                            " > ".join([f"[{k}]" for k,_ in top[:3]]))
        threading.Thread(target=_scan, daemon=True).start()

    def _frp_wizard(self):
        serial = self._get_serial()
        info   = get_device_info(serial) if serial else {}
        scores = score_methods_for_device(info) if info else []

        win = tk.Toplevel(self.root)
        win.title("FRP Bypass Wizard")
        win.geometry("640x520")
        win.configure(bg=BG)

        tk.Label(win, text="FRP BYPASS WIZARD",
                 font=("Courier", 14, "bold"),
                 bg=BG, fg=BLOOD2).pack(pady=(16,4))

        brand   = info.get("Brand","Unknown")
        model   = info.get("Model","Unknown")
        android = info.get("Android","?")

        tk.Label(win, text=f"Device: {brand} {model}  Android {android}",
                 font=("Courier", 10),
                 bg=BG, fg=GOLD).pack()

        tk.Label(win,
                 text="Recommended methods in order of success probability:",
                 font=("Courier", 9), bg=BG, fg=GREY).pack(pady=(8,4))

        frame = tk.Frame(win, bg=BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        display_methods = [(k,s) for k,s in scores[:5]] if scores else \
                          [(k, {"score":50,"reason":"generic"})
                           for k in list(FRP_METHODS.keys())[:5]]

        for i, (key, score_info) in enumerate(display_methods, 1):
            m = ALL_FRP_METHODS.get(key, {})
            if not m: continue
            sc = score_info.get("score", 50)
            color = GREEN if sc >= 75 else GOLD if sc >= 50 else GREY

            row = tk.Frame(frame, bg=BG3, pady=6, padx=10)
            row.pack(fill=tk.X, pady=2)

            tk.Label(row, text=f"Step {i}  [{key}]  {m.get('name','')}",
                     font=("Courier", 10, "bold"),
                     bg=BG3, fg=color).pack(anchor=tk.W)
            tk.Label(row, text=f"         Success probability: {sc}%  |  {score_info.get('reason','')}",
                     font=("Courier", 9),
                     bg=BG3, fg=GREY).pack(anchor=tk.W)

            def run_step(k=key, w=win):
                if ALL_FRP_METHODS.get(k,{}).get("manual"):
                    self._frp_show_guide(k)
                else:
                    self._run_frp(k)

            tk.Button(row, text="run this step",
                      font=("Courier", 9),
                      bg=BLOOD, fg=WHITE, relief=tk.FLAT,
                      pady=2, padx=8,
                      command=run_step).pack(anchor=tk.E, pady=2)

        tk.Button(win, text="close wizard",
                  font=("Courier", 10),
                  bg=BG3, fg=GREY, relief=tk.FLAT,
                  pady=4,
                  command=win.destroy).pack(pady=8)

    def _frp_show_guide(self, key):
        m = FRP_EXTENDED.get(key) or FRP_METHODS.get(key)
        if not m: return
        win = tk.Toplevel(self.root)
        win.title(f"Guide: {m['name']}")
        win.geometry("620x480")
        win.configure(bg=BG)

        tk.Label(win, text=m["name"],
                 font=("Courier", 11, "bold"),
                 bg=BG, fg=BLOOD2, wraplength=580).pack(
                     pady=(12,4), padx=12)
        tk.Label(win, text=m["desc"],
                 font=("Courier", 9, "italic"),
                 bg=BG, fg=GREY, wraplength=580).pack(padx=12)

        if m.get("warning"):
            tk.Label(win, text=f"WARNING: {m['warning']}",
                     font=("Courier", 9, "bold"),
                     bg=BG, fg=GOLD).pack(pady=4)

        txt = scrolledtext.ScrolledText(win,
            font=("Courier", 10), bg=BG2, fg=LAVENDER,
            relief=tk.FLAT, wrap=tk.WORD, height=14,
            state=tk.DISABLED)
        txt.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        txt.config(state=tk.NORMAL)

        steps = m.get("steps", [])
        if steps:
            txt.insert(tk.END, "STEP BY STEP:\n\n", )
            for i, step in enumerate(steps, 1):
                txt.insert(tk.END, f"  {i}.  {step}\n\n")
        if m.get("post"):
            txt.insert(tk.END, f"\nNEXT: {m['post']}\n")
        txt.config(state=tk.DISABLED)

        if m.get("cmds"):
            tk.Button(win, text="RUN ADB COMMANDS",
                      font=("Courier", 10, "bold"),
                      bg=BLOOD, fg=WHITE, relief=tk.FLAT,
                      pady=6,
                      command=lambda: [self._run_frp(key), win.destroy()]
                      ).pack(pady=(0,8))

        tk.Button(win, text="close",
                  font=("Courier", 9),
                  bg=BG3, fg=GREY, relief=tk.FLAT,
                  command=win.destroy).pack(pady=(0,8))

    def _frp_load_audit(self):
        self.frp_audit_txt.config(state=tk.NORMAL)
        self.frp_audit_txt.delete("1.0", tk.END)
        try:
            if os.path.exists(AUDIT_FILE):
                with open(AUDIT_FILE) as f:
                    lines = f.readlines()
                for line in lines[-100:]:  # last 100 entries
                    self.frp_audit_txt.insert(tk.END, line)
            else:
                self.frp_audit_txt.insert(tk.END,
                    "no audit log yet -- run some FRP methods to populate\n")
        except Exception as e:
            self.frp_audit_txt.insert(tk.END, f"error reading log: {e}\n")
        self.frp_audit_txt.config(state=tk.DISABLED)
        self.frp_audit_txt.see(tk.END)

    # ----------------------------------------------------------
    # BLOAT TAB
    # ----------------------------------------------------------

    def _build_bloat_tab(self):
        tk.Label(self.tab_bloat,
                 text="BLOATWARE REMOVAL  --  safe pm uninstall --user 0  (reversible)",
                 font=("Courier", 11, "bold"),
                 bg=BG, fg=BLOOD2).pack(anchor=tk.W, padx=12, pady=(10, 6))

        for profile, pkgs in BLOAT.items():
            row = tk.Frame(self.tab_bloat, bg=BG3, pady=8, padx=10)
            row.pack(fill=tk.X, pady=3, padx=8)

            tk.Label(row, text=f"{profile}  ({len(pkgs)} packages)",
                     font=("Courier", 10, "bold"),
                     bg=BG3, fg=VIOLET).pack(side=tk.LEFT)

            tk.Button(row, text="NUKE",
                      font=("Courier", 10, "bold"),
                      bg=ROYAL, fg=WHITE, relief=tk.FLAT,
                      width=8, pady=4,
                      activebackground=VIOLET, activeforeground=WHITE,
                      command=lambda p=profile, k=pkgs: self._run_bloat(p, k)).pack(
                          side=tk.RIGHT, padx=4)

        # all profiles
        allrow = tk.Frame(self.tab_bloat, bg=BG2, pady=8, padx=10)
        allrow.pack(fill=tk.X, pady=6, padx=8)
        tk.Label(allrow, text="ALL profiles",
                 font=("Courier", 10, "bold"),
                 bg=BG2, fg=BLOOD2).pack(side=tk.LEFT)
        tk.Button(allrow, text="NUKE ALL",
                  font=("Courier", 10, "bold"),
                  bg=BLOOD, fg=WHITE, relief=tk.FLAT,
                  width=10, pady=4,
                  command=self._run_bloat_all).pack(side=tk.RIGHT, padx=4)

        # custom
        tk.Label(self.tab_bloat, text="Custom package:",
                 font=("Courier", 10), bg=BG, fg=GREY).pack(
                     anchor=tk.W, padx=12, pady=(12, 2))

        custom_row = tk.Frame(self.tab_bloat, bg=BG)
        custom_row.pack(fill=tk.X, padx=12, pady=2)
        self.custom_pkg = tk.Entry(custom_row, font=("Courier", 10),
                                    bg=BG3, fg=WHITE, insertbackground=WHITE,
                                    relief=tk.FLAT, width=40)
        self.custom_pkg.pack(side=tk.LEFT, padx=(0, 8), ipady=4)
        tk.Button(custom_row, text="remove",
                  font=("Courier", 10),
                  bg=ROYAL, fg=WHITE, relief=tk.FLAT,
                  command=self._run_custom_bloat).pack(side=tk.LEFT)

        tk.Label(self.tab_bloat,
                 text="restore any package: adb shell pm install-existing <package>",
                 font=("Courier", 9), bg=BG, fg=GREY).pack(
                     anchor=tk.W, padx=12, pady=(8, 0))

    # ----------------------------------------------------------
    # WIRELESS TAB
    # ----------------------------------------------------------

    def _build_wireless_tab(self):
        tk.Label(self.tab_wireless, text="WIRELESS ADB",
                 font=("Courier", 11, "bold"),
                 bg=BG, fg=BLOOD2).pack(anchor=tk.W, padx=12, pady=(10, 6))

        actions = [
            ("Enable tcpip:5555  (Android 10 and below, USB first)", self._w_tcpip),
            ("Connect by IP",                                         self._w_connect_ip),
            ("Pair with code  (Android 11+  -- Wireless Debugging)", self._w_pair),
            ("Get device IP address",                                 self._w_get_ip),
            ("Disconnect all wireless",                               self._w_disconnect),
        ]
        for label, fn in actions:
            row = tk.Frame(self.tab_wireless, bg=BG3, pady=8, padx=12)
            row.pack(fill=tk.X, pady=3, padx=8)
            tk.Label(row, text=label, font=("Courier", 10),
                     bg=BG3, fg=WHITE).pack(side=tk.LEFT)
            tk.Button(row, text="GO",
                      font=("Courier", 10, "bold"),
                      bg=ROYAL, fg=WHITE, relief=tk.FLAT,
                      width=6, pady=3,
                      activebackground=VIOLET,
                      command=fn).pack(side=tk.RIGHT, padx=4)

        # IP input
        ip_row = tk.Frame(self.tab_wireless, bg=BG)
        ip_row.pack(fill=tk.X, padx=12, pady=(12, 2))
        tk.Label(ip_row, text="IP:port > ", font=("Courier", 10),
                 bg=BG, fg=GREY).pack(side=tk.LEFT)
        self.ip_entry = tk.Entry(ip_row, font=("Courier", 10),
                                  bg=BG3, fg=WHITE, insertbackground=WHITE,
                                  relief=tk.FLAT, width=24)
        self.ip_entry.insert(0, "192.168.x.x:5555")
        self.ip_entry.pack(side=tk.LEFT, padx=6, ipady=4)

    # ----------------------------------------------------------
    # TOOLS TAB
    # ----------------------------------------------------------

    def _build_tools_tab(self):
        tk.Label(self.tab_tools, text="TOOLS",
                 font=("Courier", 11, "bold"),
                 bg=BG, fg=BLOOD2).pack(anchor=tk.W, padx=12, pady=(10, 6))

        tools = [
            ("Device info dump",                    self._t_info),
            ("Reboot -- Normal",                    lambda: self._t_reboot("normal")),
            ("Reboot -- Recovery",                  lambda: self._t_reboot("recovery")),
            ("Reboot -- Bootloader / Fastboot",     lambda: self._t_reboot("bootloader")),
            ("Reboot -- Download Mode (Samsung)",   lambda: self._t_reboot("download")),
            ("Screenshot  (save to current folder)",self._t_screenshot),
            ("Enable OEM unlock flag",              self._t_oem),
            ("Enable USB debugging via ADB",        self._t_adb_enable),
            ("Install APK",                         self._t_install_apk),
            ("Custom ADB shell command",            self._t_custom_cmd),
        ]

        scroll = tk.Frame(self.tab_tools, bg=BG)
        scroll.pack(fill=tk.BOTH, expand=True, padx=8)

        for label, fn in tools:
            row = tk.Frame(scroll, bg=BG3, pady=7, padx=12)
            row.pack(fill=tk.X, pady=2, padx=4)
            tk.Label(row, text=label, font=("Courier", 10),
                     bg=BG3, fg=WHITE).pack(side=tk.LEFT)
            tk.Button(row, text="run",
                      font=("Courier", 9),
                      bg=BG2, fg=VIOLET, relief=tk.FLAT,
                      width=6, pady=2,
                      activebackground=ROYAL, activeforeground=WHITE,
                      command=fn).pack(side=tk.RIGHT, padx=4)

    # ----------------------------------------------------------
    # AI TAB
    # ----------------------------------------------------------

    # ----------------------------------------------------------
    # TERMINAL TAB -- built-in shell emulator
    # ----------------------------------------------------------

    def _build_term_tab(self):
        tk.Label(self.tab_term,
                 text="TERMINAL  --  adb shell / system commands",
                 font=("Courier", 11, "bold"),
                 bg=BG, fg=BLOOD2).pack(anchor=tk.W, padx=12, pady=(10, 4))

        # quick command buttons
        qbar = tk.Frame(self.tab_term, bg=BG)
        qbar.pack(fill=tk.X, padx=8, pady=(0, 4))

        quick = [
            ("adb devices",              "adb devices"),
            ("adb shell",                None),  # opens interactive
            ("logcat",                   "adb logcat -v brief"),
            ("ps list",                  "adb shell ps -A"),
            ("getprop",                  "adb shell getprop"),
            ("pm list pkgs",             "adb shell pm list packages"),
            ("fastboot devices",         "fastboot devices"),
            ("fastboot oem unlock",      "fastboot oem unlock"),
            ("clear screen",             "CLEAR"),
        ]
        # wrap in scrollable row
        qframe = tk.Frame(qbar, bg=BG)
        qframe.pack(fill=tk.X)
        for label, cmd in quick:
            tk.Button(qframe, text=label,
                      font=("Courier", 8),
                      bg=BG3, fg=VIOLET,
                      relief=tk.FLAT, padx=6, pady=3,
                      activebackground=ROYAL, activeforeground=WHITE,
                      command=lambda c=cmd, l=label: self._term_quick(c, l)
                      ).pack(side=tk.LEFT, padx=2, pady=2)

        # output area
        self.term_out = scrolledtext.ScrolledText(
            self.tab_term,
            font=("Courier New", 10),
            bg="#020208", fg=GREEN,
            insertbackground=GREEN,
            selectbackground=ROYAL,
            relief=tk.FLAT,
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        self.term_out.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # colour tags
        self.term_out.tag_config("prompt",  foreground=BLOOD2)
        self.term_out.tag_config("output",  foreground=GREEN)
        self.term_out.tag_config("error",   foreground=BLOOD)
        self.term_out.tag_config("info",    foreground=VIOLET)
        self.term_out.tag_config("cmd",     foreground=GOLD)

        # input row
        in_row = tk.Frame(self.tab_term, bg=BG)
        in_row.pack(fill=tk.X, padx=8, pady=(0, 4))

        # mode selector
        self.term_mode = tk.StringVar(value="adb shell")
        mode_menu = ttk.Combobox(
            in_row, textvariable=self.term_mode,
            values=["adb shell", "adb", "fastboot", "system", "python"],
            width=12, font=("Courier", 10), state="readonly",
        )
        mode_menu.pack(side=tk.LEFT, padx=(0, 6))

        self.term_input = tk.Entry(
            in_row, font=("Courier", 11),
            bg=BG3, fg=WHITE,
            insertbackground=WHITE,
            relief=tk.FLAT,
        )
        self.term_input.pack(side=tk.LEFT, fill=tk.X, expand=True,
                              padx=(0, 6), ipady=6)
        self.term_input.bind("<Return>",   lambda e: self._term_run())
        self.term_input.bind("<Up>",       lambda e: self._term_history(-1))
        self.term_input.bind("<Down>",     lambda e: self._term_history(1))
        self.term_input.bind("<Tab>",      lambda e: self._term_tab_complete())

        tk.Button(in_row, text="run",
                  font=("Courier", 10, "bold"),
                  bg=BLOOD, fg=WHITE, relief=tk.FLAT,
                  width=5, pady=4,
                  activebackground=BLOOD2,
                  command=self._term_run).pack(side=tk.LEFT, padx=(0, 4))

        tk.Button(in_row, text="kill",
                  font=("Courier", 10),
                  bg=BG3, fg=GREY, relief=tk.FLAT,
                  width=5, pady=4,
                  command=self._term_kill).pack(side=tk.LEFT)

        # state
        self._term_history_list = []
        self._term_history_idx  = 0
        self._term_proc         = None

        # welcome message
        self._term_write("SoulWoRn Terminal -- built-in shell emulator\n", "info")
        self._term_write(f"adb path: {ADB_PATH}\n", "info")
        self._term_write(f"fastboot: {_fastboot_path()}\n", "info")
        self._term_write("modes: adb shell / adb / fastboot / system / python\n", "info")
        self._term_write("up/down = history  |  tab = complete  |  kill = stop process\n\n", "info")
        self._term_prompt()

    def _term_write(self, text, tag="output"):
        self.term_out.config(state=tk.NORMAL)
        self.term_out.insert(tk.END, text, tag)
        self.term_out.see(tk.END)
        self.term_out.config(state=tk.DISABLED)

    def _term_prompt(self):
        serial = self._get_serial() or "no-device"
        mode   = self.term_mode.get()
        self._term_write(f"\n[{mode}][{serial}] $ ", "prompt")

    def _term_quick(self, cmd, label):
        if cmd == "CLEAR":
            self.term_out.config(state=tk.NORMAL)
            self.term_out.delete("1.0", tk.END)
            self.term_out.config(state=tk.DISABLED)
            self._term_prompt()
            return
        if cmd is None:
            # open real terminal window
            self._term_open_external()
            return
        self.term_input.delete(0, tk.END)
        self.term_input.insert(0, cmd)
        # auto-set mode
        if cmd.startswith("adb shell"):
            self.term_mode.set("adb shell")
            self.term_input.delete(0, tk.END)
            self.term_input.insert(0, cmd.replace("adb shell ", ""))
        elif cmd.startswith("adb "):
            self.term_mode.set("adb")
            self.term_input.delete(0, tk.END)
            self.term_input.insert(0, cmd.replace("adb ", ""))
        elif cmd.startswith("fastboot"):
            self.term_mode.set("fastboot")
            self.term_input.delete(0, tk.END)
            self.term_input.insert(0, cmd.replace("fastboot ", ""))
        self._term_run()

    def _term_run(self):
        raw   = self.term_input.get().strip()
        if not raw: return
        mode  = self.term_mode.get()
        serial= self._get_serial()

        # history
        self._term_history_list.append(raw)
        self._term_history_idx = len(self._term_history_list)
        self.term_input.delete(0, tk.END)

        self._term_write(f"{raw}\n", "cmd")

        def _run():
            try:
                # build command based on mode
                if mode == "adb shell":
                    prefix = [ADB_PATH, "-s", serial] if serial else [ADB_PATH]
                    cmd = prefix + ["shell"] + raw.split()
                elif mode == "adb":
                    prefix = [ADB_PATH, "-s", serial] if serial else [ADB_PATH]
                    cmd = prefix + raw.split()
                elif mode == "fastboot":
                    cmd = [_fastboot_path()] + raw.split()
                elif mode == "python":
                    cmd = [sys.executable, "-c", raw]
                else:  # system
                    if sys.platform == "win32":
                        cmd = ["cmd", "/c"] + raw.split()
                    else:
                        cmd = ["/bin/sh", "-c", raw]

                self._term_proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )

                for line in iter(self._term_proc.stdout.readline, ""):
                    if line:
                        tag = "error" if any(
                            w in line.lower() for w in
                            ["error","fail","denied","exception","not found"]
                        ) else "output"
                        self.term_out.after(0,
                            lambda l=line, t=tag: self._term_write(l, t))

                self._term_proc.wait()
                rc = self._term_proc.returncode
                if rc != 0:
                    self.term_out.after(0,
                        lambda: self._term_write(f"[exit {rc}]\n", "error"))

            except FileNotFoundError as e:
                self.term_out.after(0,
                    lambda: self._term_write(f"not found: {e}\n", "error"))
            except Exception as e:
                self.term_out.after(0,
                    lambda: self._term_write(f"error: {e}\n", "error"))
            finally:
                self._term_proc = None
                self.term_out.after(0, self._term_prompt)

        threading.Thread(target=_run, daemon=True).start()

    def _term_kill(self):
        if self._term_proc:
            try:
                self._term_proc.terminate()
                self._term_write("\n[killed]\n", "error")
            except Exception:
                pass
        else:
            self._term_write("[no process running]\n", "info")

    def _term_history(self, direction):
        if not self._term_history_list: return
        self._term_history_idx = max(0, min(
            len(self._term_history_list) - 1,
            self._term_history_idx + direction
        ))
        self.term_input.delete(0, tk.END)
        self.term_input.insert(0,
            self._term_history_list[self._term_history_idx])

    def _term_tab_complete(self):
        """Tab complete common ADB commands."""
        current = self.term_input.get()
        mode    = self.term_mode.get()
        completions = {
            "adb shell": [
                "getprop ", "setprop ", "pm list packages",
                "pm uninstall -k --user 0 ",
                "pm install-existing ",
                "am start -n ", "am force-stop ",
                "settings put global ", "settings put secure ",
                "content insert --uri content://settings/secure ",
                "screencap -p /sdcard/screen.png",
                "dumpsys battery", "dumpsys usb",
                "reboot", "reboot recovery", "reboot bootloader",
                "reboot download",
                "ip addr show wlan0",
                "ps -A", "ls /sdcard/",
            ],
            "adb": [
                "devices", "shell", "reboot", "reboot recovery",
                "reboot bootloader", "reboot download",
                "tcpip 5555", "connect ", "disconnect",
                "push ", "pull ", "install ", "sideload ",
                "logcat", "bugreport",
            ],
            "fastboot": [
                "devices", "erase frp", "erase userdata",
                "reboot", "reboot bootloader",
                "flash boot ", "flash recovery ",
                "oem unlock", "flashing unlock",
                "getvar all",
            ],
        }
        opts = [c for c in completions.get(mode, [])
                if c.startswith(current)]
        if len(opts) == 1:
            self.term_input.delete(0, tk.END)
            self.term_input.insert(0, opts[0])
        elif len(opts) > 1:
            self._term_write("\n" + "  ".join(opts) + "\n", "info")
            self._term_prompt()
        return "break"

    def _term_open_external(self):
        """Open a real system terminal window."""
        try:
            if sys.platform == "win32":
                subprocess.Popen(["cmd", "/k",
                    f"echo SoulWoRn Terminal && "
                    f"set PATH=%PATH%;{os.path.dirname(ADB_PATH)} && "
                    f"echo adb path: {ADB_PATH} && "
                    f"echo type adb devices to start"])
            else:
                for term in ["xterm", "gnome-terminal", "konsole", "xfce4-terminal"]:
                    if shutil.which(term):
                        subprocess.Popen([term])
                        break
        except Exception as e:
            self._log(f"could not open terminal: {e}")

    # ----------------------------------------------------------
    # ODIN HELPER TAB
    # ----------------------------------------------------------

    def _build_odin_tab(self):
        tk.Label(self.tab_odin,
                 text="ODIN / FLASH HELPER  --  Samsung firmware",
                 font=("Courier", 11, "bold"),
                 bg=BG, fg=BLOOD2).pack(anchor=tk.W, padx=12, pady=(10,4))

        # auto-detect model
        hdr = tk.Frame(self.tab_odin, bg=BG)
        hdr.pack(fill=tk.X, padx=12, pady=(0,6))
        tk.Label(hdr, text="model:", font=("Courier",10),
                 bg=BG, fg=GREY).pack(side=tk.LEFT)
        self.odin_model_var = tk.StringVar(value="SM-S911W")
        model_e = tk.Entry(hdr, textvariable=self.odin_model_var,
                           font=("Courier",10), bg=BG3, fg=GOLD,
                           insertbackground=WHITE, relief=tk.FLAT, width=16)
        model_e.pack(side=tk.LEFT, padx=6, ipady=3)
        tk.Button(hdr, text="read from device",
                  font=("Courier",9), bg=BG3, fg=VIOLET,
                  relief=tk.FLAT, padx=6,
                  command=self._odin_read_model).pack(side=tk.LEFT, padx=4)
        tk.Button(hdr, text="open samfw.com",
                  font=("Courier",9), bg=BLOOD, fg=WHITE,
                  relief=tk.FLAT, padx=6,
                  command=self._odin_open_samfw).pack(side=tk.LEFT, padx=4)
        tk.Button(hdr, text="open samfrew.com",
                  font=("Courier",9), bg=ROYAL, fg=WHITE,
                  relief=tk.FLAT, padx=6,
                  command=self._odin_open_samfrew).pack(side=tk.LEFT, padx=4)

        # download mode guide
        sep_frame = tk.Frame(self.tab_odin, bg=BG2, pady=8, padx=12)
        sep_frame.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(sep_frame, text="ENTER DOWNLOAD MODE",
                 font=("Courier",10,"bold"), bg=BG2, fg=BLOOD2).pack(anchor=tk.W)

        dm_methods = [
            ("S20 / S21 / S22 / S23 / S24 / S25",
             "Power off > hold Vol Down > plug USB cable"),
            ("S10 / Note 10 / older with Bixby btn",
             "Power off > hold Vol Down + Bixby + Power"),
            ("Any Samsung via ADB",
             "adb reboot download"),
            ("Any Samsung powered on",
             "hold Vol Down + Vol Up while plugging USB"),
        ]
        for model, method in dm_methods:
            row = tk.Frame(sep_frame, bg=BG2)
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=f"  {model}:",
                     font=("Courier",9,"bold"),
                     bg=BG2, fg=VIOLET, width=38, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, text=method,
                     font=("Courier",9),
                     bg=BG2, fg=LAVENDER, anchor=tk.W).pack(side=tk.LEFT)
            if "adb" in method.lower():
                tk.Button(row, text="run",
                          font=("Courier",8), bg=BG3, fg=GREY,
                          relief=tk.FLAT, padx=4,
                          command=lambda: self._term_quick(
                              "adb reboot download", "reboot download")
                          ).pack(side=tk.RIGHT, padx=4)

        # Odin slot guide
        slot_frame = tk.Frame(self.tab_odin, bg=BG3, pady=8, padx=12)
        slot_frame.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(slot_frame, text="ODIN SLOT GUIDE",
                 font=("Courier",10,"bold"), bg=BG3, fg=BLOOD2).pack(anchor=tk.W)

        slots = [
            ("BL",   "Bootloader",    "flash only when updating bootloader"),
            ("AP",   "Main firmware", "largest file -- core OS"),
            ("CP",   "Modem/Baseband","radio firmware"),
            ("CSC",  "Full wipe CSC", "WARNING: wipes all data"),
            ("HOME_CSC", "Keep-data CSC", "preserves user data -- USE THIS"),
        ]
        for slot, name, note in slots:
            row = tk.Frame(slot_frame, bg=BG3)
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=f"  {slot:<12}",
                     font=("Courier",10,"bold"),
                     bg=BG3, fg=GOLD).pack(side=tk.LEFT)
            tk.Label(row, text=f"{name:<20}",
                     font=("Courier",9),
                     bg=BG3, fg=WHITE).pack(side=tk.LEFT)
            color = BLOOD if "wipe" in note.lower() else GREY
            tk.Label(row, text=note,
                     font=("Courier",9,"italic"),
                     bg=BG3, fg=color).pack(side=tk.LEFT)

        # Odin settings guide
        settings_frame = tk.Frame(self.tab_odin, bg=BG2, pady=8, padx=12)
        settings_frame.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(settings_frame, text="ODIN OPTIONS (Options tab)",
                 font=("Courier",10,"bold"), bg=BG2, fg=BLOOD2).pack(anchor=tk.W)

        odin_opts = [
            ("Auto Reboot",     "ON",  "reboots after flash"),
            ("F. Reset Time",   "ON",  "resets flash counter"),
            ("Re-Partition",    "OFF", "KEEP OFF unless replacing partition table"),
            ("Nand Erase All",  "OFF", "KEEP OFF -- bricks if wrong firmware"),
        ]
        for opt, val, note in odin_opts:
            row = tk.Frame(settings_frame, bg=BG2)
            row.pack(fill=tk.X, pady=1)
            color = GREEN if val == "ON" else BLOOD
            tk.Label(row, text=f"  {opt:<20}",
                     font=("Courier",9),
                     bg=BG2, fg=WHITE).pack(side=tk.LEFT)
            tk.Label(row, text=f"{val:<8}",
                     font=("Courier",9,"bold"),
                     bg=BG2, fg=color).pack(side=tk.LEFT)
            tk.Label(row, text=note,
                     font=("Courier",9,"italic"),
                     bg=BG2, fg=GREY).pack(side=tk.LEFT)

        # ADB reboot to download shortcut
        btn_row = tk.Frame(self.tab_odin, bg=BG)
        btn_row.pack(fill=tk.X, padx=12, pady=8)
        tk.Button(btn_row, text="adb reboot download",
                  font=("Courier",10,"bold"),
                  bg=BLOOD, fg=WHITE, relief=tk.FLAT,
                  pady=6, padx=12,
                  command=lambda: self._term_quick(
                      "adb reboot download","reboot download")
                  ).pack(side=tk.LEFT, padx=(0,8))
        tk.Button(btn_row, text="adb reboot recovery",
                  font=("Courier",10),
                  bg=ROYAL, fg=WHITE, relief=tk.FLAT,
                  pady=6, padx=12,
                  command=lambda: self._term_quick(
                      "adb reboot recovery","reboot recovery")
                  ).pack(side=tk.LEFT, padx=(0,8))
        tk.Button(btn_row, text="adb reboot bootloader",
                  font=("Courier",10),
                  bg=BG3, fg=VIOLET, relief=tk.FLAT,
                  pady=6, padx=12,
                  command=lambda: self._term_quick(
                      "adb reboot bootloader","reboot bootloader")
                  ).pack(side=tk.LEFT)

    def _odin_read_model(self):
        serial = self._get_serial()
        if not serial:
            self._ghost_say("connect device first")
            return
        _, val, _ = adb("-s", serial, "shell", "getprop ro.product.model")
        if val:
            self.odin_model_var.set(val.strip())
            self._log(f"odin model: {val.strip()}")
            self._ghost_say(f"model set: {val.strip()}")

    def _odin_open_samfw(self):
        model = self.odin_model_var.get().strip()
        url   = f"https://samfw.com/firmware/{model}"
        import webbrowser
        webbrowser.open(url)
        self._log(f"opened samfw: {url}")

    def _odin_open_samfrew(self):
        model = self.odin_model_var.get().strip()
        url   = f"https://samfrew.com/?model={model}"
        import webbrowser
        webbrowser.open(url)

    # ----------------------------------------------------------
    # SIDELOAD ZIP BUILDER TAB
    # ----------------------------------------------------------

    def _build_zip_tab(self):
        import zipfile as _zf

        # ── tab notebook ──────────────────────────────────────────────────────
        zip_nb = ttk.Notebook(self.tab_zip)
        zip_nb.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self._ztab_search  = tk.Frame(zip_nb, bg=BG)
        self._ztab_pull    = tk.Frame(zip_nb, bg=BG)
        self._ztab_build   = tk.Frame(zip_nb, bg=BG)
        self._ztab_unpack  = tk.Frame(zip_nb, bg=BG)

        zip_nb.add(self._ztab_search, text="  Firmware Search  ")
        zip_nb.add(self._ztab_pull,   text="  Pull from Device ")
        zip_nb.add(self._ztab_build,  text="  Build ZIP        ")
        zip_nb.add(self._ztab_unpack, text="  Unpack + Edit    ")

        self._build_ztab_search()
        self._build_ztab_pull()
        self._build_ztab_build()
        self._build_ztab_unpack()

        # shared state
        self._zip_vars      = {}
        self._fw_local_path = None
        self._fw_unpacked   = None

    # ── FIRMWARE SEARCH TAB ───────────────────────────────────────────────────

    def _build_ztab_search(self):
        p = self._ztab_search

        tk.Label(p, text="FIRMWARE SEARCH  --  samfw / samfrew / sammobile",
                 font=("Courier",11,"bold"),
                 bg=BG, fg=BLOOD2).pack(anchor=tk.W, padx=12, pady=(10,4))

        # model + region row
        row1 = tk.Frame(p, bg=BG)
        row1.pack(fill=tk.X, padx=12, pady=4)

        tk.Label(row1, text="model:",
                 font=("Courier",10), bg=BG, fg=GREY).pack(side=tk.LEFT)
        self.fw_model = tk.StringVar(value="SM-S911W")
        tk.Entry(row1, textvariable=self.fw_model,
                 font=("Courier",10), bg=BG3, fg=GOLD,
                 insertbackground=WHITE, relief=tk.FLAT, width=14
                 ).pack(side=tk.LEFT, padx=6, ipady=3)

        tk.Label(row1, text="region:",
                 font=("Courier",10), bg=BG, fg=GREY).pack(side=tk.LEFT, padx=(8,0))
        self.fw_region = tk.StringVar(value="XAC")
        region_combo = ttk.Combobox(row1, textvariable=self.fw_region,
                                     values=["XAC","XAA","BTU","DBT","KOO",
                                             "CHC","VZW","ATT","TMB","SPR",
                                             "EUR","XEF","INS","XXV"],
                                     width=6, font=("Courier",10))
        region_combo.pack(side=tk.LEFT, padx=6)

        tk.Button(row1, text="read from device",
                  font=("Courier",9), bg=BG3, fg=VIOLET,
                  relief=tk.FLAT, padx=6,
                  command=self._fw_read_model).pack(side=tk.LEFT, padx=4)

        # search buttons
        btn_row = tk.Frame(p, bg=BG)
        btn_row.pack(fill=tk.X, padx=12, pady=4)

        tk.Button(btn_row, text="SEARCH samfw.com",
                  font=("Courier",10,"bold"),
                  bg=BLOOD, fg=WHITE, relief=tk.FLAT,
                  pady=6, padx=12,
                  command=lambda: self._fw_search("samfw")
                  ).pack(side=tk.LEFT, padx=(0,6))
        tk.Button(btn_row, text="SEARCH samfrew.com",
                  font=("Courier",10,"bold"),
                  bg=ROYAL, fg=WHITE, relief=tk.FLAT,
                  pady=6, padx=12,
                  command=lambda: self._fw_search("samfrew")
                  ).pack(side=tk.LEFT, padx=(0,6))
        tk.Button(btn_row, text="open in browser",
                  font=("Courier",9), bg=BG3, fg=VIOLET,
                  relief=tk.FLAT, padx=8, pady=6,
                  command=self._fw_open_browser
                  ).pack(side=tk.LEFT)

        # results area
        tk.Label(p, text="firmware versions found:",
                 font=("Courier",9), bg=BG, fg=GREY
                 ).pack(anchor=tk.W, padx=12, pady=(8,2))

        self.fw_results = scrolledtext.ScrolledText(
            p, height=10,
            font=("Courier",9), bg="#020208", fg=GREEN,
            relief=tk.FLAT, state=tk.DISABLED,
        )
        self.fw_results.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        self.fw_results.tag_config("header",  foreground=BLOOD2)
        self.fw_results.tag_config("version", foreground=GREEN)
        self.fw_results.tag_config("info",    foreground=VIOLET)
        self.fw_results.tag_config("dl",      foreground=GOLD)

        # download bar
        dl_row = tk.Frame(p, bg=BG)
        dl_row.pack(fill=tk.X, padx=12, pady=4)

        self.fw_dl_url = tk.StringVar(value="")
        tk.Label(dl_row, text="direct URL:",
                 font=("Courier",9), bg=BG, fg=GREY).pack(side=tk.LEFT)
        tk.Entry(dl_row, textvariable=self.fw_dl_url,
                 font=("Courier",8), bg=BG3, fg=GOLD,
                 insertbackground=WHITE, relief=tk.FLAT, width=40
                 ).pack(side=tk.LEFT, padx=6, ipady=2)
        tk.Button(dl_row, text="DOWNLOAD",
                  font=("Courier",9,"bold"),
                  bg=BLOOD, fg=WHITE, relief=tk.FLAT, padx=8,
                  command=self._fw_download).pack(side=tk.LEFT)
        tk.Button(dl_row, text="browse local file",
                  font=("Courier",9), bg=BG3, fg=VIOLET,
                  relief=tk.FLAT, padx=8,
                  command=self._fw_browse_local).pack(side=tk.LEFT, padx=4)

        self.fw_dl_progress = tk.Label(
            p, text="", font=("Courier",9),
            bg=BG, fg=GREEN)
        self.fw_dl_progress.pack(anchor=tk.W, padx=12, pady=2)

    def _fw_read_model(self):
        serial = self._get_serial()
        if not serial: return
        _, m, _ = adb("-s",serial,"shell","getprop ro.product.model")
        _, r, _ = adb("-s",serial,"shell","getprop ro.csc.sales_code")
        if m: self.fw_model.set(m.strip())
        if r: self.fw_region.set(r.strip())
        self._ghost_say(f"model: {m.strip()} region: {r.strip()}")

    def _fw_results_write(self, text, tag="info"):
        self.fw_results.config(state=tk.NORMAL)
        self.fw_results.insert(tk.END, text, tag)
        self.fw_results.see(tk.END)
        self.fw_results.config(state=tk.DISABLED)

    def _fw_search(self, source):
        model  = self.fw_model.get().strip().upper()
        region = self.fw_region.get().strip().upper()
        if not model:
            self._ghost_say("enter a model number first")
            return

        self.fw_results.config(state=tk.NORMAL)
        self.fw_results.delete("1.0", tk.END)
        self.fw_results.config(state=tk.DISABLED)
        self._fw_results_write(
            f"searching {source} for {model} / {region}...\n\n", "header")
        self._ghost_say(f"searching {source} for {model} {region}...")

        def _search():
            try:
                if source == "samfw":
                    url = f"https://samfw.com/firmware/{model}/{region}"
                else:
                    url = f"https://samfrew.com/?model={model}&region={region}"

                req = urllib.request.Request(url, headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
                    )
                })
                with urllib.request.urlopen(req, timeout=15) as resp:
                    html = resp.read().decode("utf-8", errors="ignore")

                # parse firmware versions from HTML
                versions = self._fw_parse_versions(html, source, model, region)

                if versions:
                    self.root.after(0, lambda:
                        self._fw_results_write(
                            f"found {len(versions)} firmware version(s):\n\n",
                            "header"))
                    for v in versions[:15]:
                        self.root.after(0, lambda vv=v:
                            self._fw_results_write(
                                f"  {vv['version']:<30}"
                                f"  {vv.get('date',''):<14}"
                                f"  {vv.get('size','')}\n",
                                "version"))
                        if v.get("dl_url"):
                            self.root.after(0, lambda vv=v:
                                self._fw_results_write(
                                    f"    >> {vv['dl_url']}\n", "dl"))
                    self.root.after(0, lambda:
                        self._ghost_say(
                            f"found {len(versions)} versions for {model}"))
                else:
                    self.root.after(0, lambda:
                        self._fw_results_write(
                            f"no firmware versions found on {source}\n"
                            f"try: browser > {url}\n", "info"))
                    self.root.after(0, lambda:
                        self._ghost_say(
                            f"nothing found -- try opening in browser"))

            except urllib.error.HTTPError as e:
                self.root.after(0, lambda:
                    self._fw_results_write(
                        f"HTTP {e.code} -- may need browser login\n"
                        f"opening in browser instead...\n", "info"))
                self.root.after(0, self._fw_open_browser)
            except Exception as e:
                self.root.after(0, lambda:
                    self._fw_results_write(f"search error: {e}\n", "info"))

        threading.Thread(target=_search, daemon=True).start()

    def _fw_parse_versions(self, html, source, model, region):
        """Parse firmware version info from samfw/samfrew HTML."""
        import re as _re
        versions = []

        if source == "samfw":
            # samfw pattern: version strings like G991WVLS6DYF1
            pattern = _re.compile(
                r'([A-Z0-9]{4,6}[A-Z]{3}\d[A-Z]{3}\d+)'
                r'.*?(\d{4}-\d{2}-\d{2})?'
                r'.*?(\d+\.?\d*\s*[GMBT]+)?',
                _re.DOTALL
            )
            seen = set()
            for m in pattern.finditer(html):
                ver = m.group(1)
                if ver not in seen and len(ver) > 8:
                    seen.add(ver)
                    versions.append({
                        "version": ver,
                        "date":    m.group(2) or "",
                        "size":    m.group(3) or "",
                        "dl_url":  f"https://samfw.com/firmware/{model}/{region}/{ver}"
                    })
        else:
            # samfrew pattern
            pattern = _re.compile(
                r'firmware[_\-]version["\s:>]+([A-Z0-9]+)',
                _re.IGNORECASE
            )
            for m in pattern.finditer(html):
                versions.append({
                    "version": m.group(1),
                    "dl_url": ""
                })

        # also look for direct download links
        dl_pattern = _re.compile(
            r'href=["\']([^"\']*\.zip[^"\']*|[^"\']*\.tar[^"\']*\.md5[^"\']*)["\']',
            _re.IGNORECASE
        )
        dl_links = [m.group(1) for m in dl_pattern.finditer(html)]
        if dl_links and not versions:
            for link in dl_links[:5]:
                versions.append({"version": os.path.basename(link),
                                  "dl_url": link, "date":"", "size":""})

        return versions

    def _fw_open_browser(self):
        import webbrowser
        model  = self.fw_model.get().strip().upper()
        region = self.fw_region.get().strip().upper()
        webbrowser.open(f"https://samfw.com/firmware/{model}/{region}")

    def _fw_download(self):
        url = self.fw_dl_url.get().strip()
        if not url:
            messagebox.showinfo("download", "paste a direct download URL first")
            return

        dl_dir = os.path.join(
            os.environ.get("USERPROFILE", os.path.expanduser("~")),
            "Downloads")
        fname = os.path.basename(url.split("?")[0]) or "firmware.zip"
        out_path = os.path.join(dl_dir, fname)

        self._ghost_say(f"downloading: {fname}")
        self.fw_dl_progress.config(text=f"downloading {fname}...", fg=GOLD)

        def _dl():
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 Chrome/120.0.0.0"
                    ),
                    "Referer": "https://samfw.com/",
                })
                total = 0
                with urllib.request.urlopen(req, timeout=60) as resp, \
                     open(out_path, "wb") as f:
                    content_len = resp.headers.get("Content-Length")
                    cl = int(content_len) if content_len else 0
                    while True:
                        chunk = resp.read(65536)
                        if not chunk: break
                        f.write(chunk)
                        total += len(chunk)
                        if cl:
                            pct = total / cl * 100
                            self.root.after(0, lambda p=pct, t=total:
                                self.fw_dl_progress.config(
                                    text=f"downloading... {p:.1f}%  "
                                         f"({t//1024//1024}MB)",
                                    fg=GOLD))

                self._fw_local_path = out_path
                self.root.after(0, lambda:
                    self.fw_dl_progress.config(
                        text=f"saved: {out_path}", fg=GREEN))
                self.root.after(0, lambda:
                    self._ghost_say(f"firmware downloaded: {fname}"))
                self.root.after(0, lambda:
                    self._log(f"fw downloaded: {out_path}"))

            except Exception as e:
                self.root.after(0, lambda:
                    self.fw_dl_progress.config(
                        text=f"download failed: {e}", fg=BLOOD))
                self.root.after(0, lambda:
                    self._ghost_say("download failed -- try browser"))

        threading.Thread(target=_dl, daemon=True).start()

    def _fw_browse_local(self):
        path = filedialog.askopenfilename(
            title="select firmware file",
            filetypes=[
                ("Samsung firmware", "*.zip *.tar *.md5 *.tar.md5"),
                ("All files", "*.*"),
            ]
        )
        if path:
            self._fw_local_path = path
            self.fw_dl_progress.config(
                text=f"local: {path}", fg=GREEN)
            self._ghost_say(f"firmware loaded: {os.path.basename(path)}")
            self._log(f"fw local: {path}")

    # ── PULL FROM DEVICE TAB ──────────────────────────────────────────────────

    def _build_ztab_pull(self):
        p = self._ztab_pull

        tk.Label(p, text="PULL FROM DEVICE  --  extract files from connected phone",
                 font=("Courier",11,"bold"),
                 bg=BG, fg=BLOOD2).pack(anchor=tk.W, padx=12, pady=(10,4))

        info_lbl = tk.Label(p,
            text="pulls key system files directly from connected device via ADB",
            font=("Courier",9,"italic"), bg=BG, fg=GREY)
        info_lbl.pack(anchor=tk.W, padx=12, pady=(0,6))

        # pull targets
        targets_frame = tk.Frame(p, bg=BG3, padx=12, pady=8)
        targets_frame.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(targets_frame, text="select files to pull:",
                 font=("Courier",10,"bold"),
                 bg=BG3, fg=VIOLET).pack(anchor=tk.W, pady=(0,6))

        self._pull_targets = {}
        pull_items = [
            ("build.prop (system)",       "/system/build.prop",          True),
            ("build.prop (vendor)",       "/vendor/build.prop",          True),
            ("build.prop (product)",      "/product/build.prop",         False),
            ("settings.db (FRP flags)",
             "/data/data/com.google.android.providers.settings"
             "/databases/settings.db",                                   True),
            ("FactoryApp/a (FRP account)","/efs/FactoryApp/a",           True),
            ("FactoryApp/b (FRP account)","/efs/FactoryApp/b",           True),
            ("framework.jar",             "/system/framework/framework.jar", False),
            ("services.jar",              "/system/framework/services.jar",  False),
            ("bootanimation.zip",         "/system/media/bootanimation.zip", False),
            ("recovery.img",              "/dev/block/by-name/recovery",     False),
            ("frp partition",             "/dev/block/by-name/frp",          True),
        ]
        for label, path, default in pull_items:
            var = tk.BooleanVar(value=default)
            self._pull_targets[path] = var
            row = tk.Frame(targets_frame, bg=BG3)
            row.pack(anchor=tk.W, pady=1)
            tk.Checkbutton(row, text=f"{label}",
                           variable=var,
                           font=("Courier",9),
                           bg=BG3, fg=LAVENDER,
                           selectcolor=BG2,
                           activebackground=BG3
                           ).pack(side=tk.LEFT)
            tk.Label(row, text=f"  {path}",
                     font=("Courier",8),
                     bg=BG3, fg=GREY).pack(side=tk.LEFT)

        # output dir
        out_row = tk.Frame(p, bg=BG)
        out_row.pack(fill=tk.X, padx=12, pady=6)
        tk.Label(out_row, text="save to:",
                 font=("Courier",10), bg=BG, fg=GREY).pack(side=tk.LEFT)
        pull_default = os.path.join(
            os.environ.get("USERPROFILE", os.path.expanduser("~")),
            "Downloads", "soulworn_pull")
        self.pull_outdir = tk.StringVar(value=pull_default)
        tk.Entry(out_row, textvariable=self.pull_outdir,
                 font=("Courier",9), bg=BG3, fg=WHITE,
                 insertbackground=WHITE, relief=tk.FLAT, width=36
                 ).pack(side=tk.LEFT, padx=6, ipady=3)
        tk.Button(out_row, text="browse",
                  font=("Courier",9), bg=BG3, fg=VIOLET,
                  relief=tk.FLAT,
                  command=lambda: self.pull_outdir.set(
                      filedialog.askdirectory() or self.pull_outdir.get())
                  ).pack(side=tk.LEFT)

        # pull button
        btn_row = tk.Frame(p, bg=BG)
        btn_row.pack(fill=tk.X, padx=12, pady=4)
        tk.Button(btn_row, text="PULL SELECTED FILES",
                  font=("Courier",11,"bold"),
                  bg=BLOOD, fg=WHITE, relief=tk.FLAT,
                  pady=8, padx=16,
                  command=self._fw_pull_files).pack(side=tk.LEFT)
        tk.Button(btn_row, text="pull + open unpack tab",
                  font=("Courier",10),
                  bg=ROYAL, fg=WHITE, relief=tk.FLAT,
                  pady=8, padx=12,
                  command=lambda: [self._fw_pull_files(),
                                   self._ztab_unpack.tkraise()]
                  ).pack(side=tk.LEFT, padx=8)

        # log
        self.pull_log = scrolledtext.ScrolledText(
            p, height=8,
            font=("Courier",9), bg="#020208", fg=GREEN,
            relief=tk.FLAT, state=tk.DISABLED,
        )
        self.pull_log.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

    def _fw_pull_files(self):
        serial  = self._get_serial()
        prefix  = ["-s", serial] if serial else []
        out_dir = self.pull_outdir.get().strip()
        os.makedirs(out_dir, exist_ok=True)

        targets = [(path, var.get())
                   for path, var in self._pull_targets.items()
                   if var.get()]

        if not targets:
            self._ghost_say("select at least one file to pull")
            return

        self._ghost_say(f"pulling {len(targets)} files...")
        self._log(f"pull: {len(targets)} files -> {out_dir}")

        def _run():
            def wlog(txt):
                self.pull_log.config(state=tk.NORMAL)
                self.pull_log.insert(tk.END, txt)
                self.pull_log.see(tk.END)
                self.pull_log.config(state=tk.DISABLED)

            ok = fail = 0
            for path, _ in targets:
                fname = path.replace("/","_").lstrip("_")
                dest  = os.path.join(out_dir, fname)
                self.root.after(0, lambda p=path:
                    wlog(f"pulling: {p}\n"))
                code, out, err = adb(*prefix, "pull", path, dest)
                if code == 0:
                    self.root.after(0, lambda d=dest:
                        wlog(f"  OK -> {d}\n"))
                    ok += 1
                else:
                    self.root.after(0, lambda e=err:
                        wlog(f"  FAIL: {e}\n"))
                    fail += 1

            self.root.after(0, lambda:
                wlog(f"\ndone: {ok} ok / {fail} failed\noutdir: {out_dir}\n"))
            self.root.after(0, lambda:
                self._ghost_say(f"pulled {ok}/{len(targets)} files"))
            self._fw_unpacked = out_dir
            audit_log("FW_PULL", f"{ok} files -> {out_dir}", serial or "")

        threading.Thread(target=_run, daemon=True).start()

    # ── BUILD ZIP TAB ─────────────────────────────────────────────────────────

    def _build_ztab_build(self):
        p = self._ztab_build

        tk.Label(p, text="BUILD SIDELOAD ZIP",
                 font=("Courier",11,"bold"),
                 bg=BG, fg=BLOOD2).pack(anchor=tk.W, padx=12, pady=(10,4))

        # auto-fill
        hdr = tk.Frame(p, bg=BG)
        hdr.pack(fill=tk.X, padx=12, pady=(0,4))
        tk.Button(hdr, text="auto-fill from device",
                  font=("Courier",9), bg=ROYAL, fg=WHITE,
                  relief=tk.FLAT, padx=8, pady=3,
                  command=self._zip_autofill).pack(side=tk.LEFT)
        self.zip_status = tk.Label(hdr, text="",
                                    font=("Courier",9), bg=BG, fg=GOLD)
        self.zip_status.pack(side=tk.LEFT, padx=8)

        # form fields
        form = tk.Frame(p, bg=BG3, padx=12, pady=8)
        form.pack(fill=tk.X, padx=8, pady=4)
        fields = [
            ("Device model",    "zip_model",   "Unknown"),
            ("Codename",        "zip_codename","generic"),
            ("Android version", "zip_android", "?"),
            ("Security patch",  "zip_patch",   "?"),
            ("Output filename", "zip_fname",   "soulworn_frp.zip"),
        ]
        self._zip_vars = {}
        for label, attr, default in fields:
            row = tk.Frame(form, bg=BG3)
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=f"{label}:",
                     font=("Courier",9), bg=BG3, fg=GREY,
                     width=20, anchor=tk.W).pack(side=tk.LEFT)
            var = tk.StringVar(value=default)
            self._zip_vars[attr] = var
            tk.Entry(row, textvariable=var,
                     font=("Courier",10), bg=BG2, fg=WHITE,
                     insertbackground=WHITE, relief=tk.FLAT, width=30
                     ).pack(side=tk.LEFT, ipady=3)

        # zip type
        type_frame = tk.Frame(p, bg=BG)
        type_frame.pack(fill=tk.X, padx=12, pady=4)
        tk.Label(type_frame, text="type:",
                 font=("Courier",10), bg=BG, fg=GREY).pack(side=tk.LEFT)
        self.zip_type = tk.StringVar(value="frp_full")
        for label, val in [
            ("FRP full",    "frp_full"),
            ("FRP+EFS",     "frp_efs"),
            ("Flags only",  "flags_only"),
            ("EFS only",    "efs_only"),
            ("Custom",      "custom"),
        ]:
            tk.Radiobutton(type_frame, text=label,
                           variable=self.zip_type, value=val,
                           font=("Courier",9), bg=BG, fg=LAVENDER,
                           selectcolor=BG3, activebackground=BG
                           ).pack(side=tk.LEFT, padx=6)

        # custom cmds
        tk.Label(p, text="custom shell commands (one per line):",
                 font=("Courier",9), bg=BG, fg=GREY
                 ).pack(anchor=tk.W, padx=12, pady=(6,2))
        self.zip_custom_txt = tk.Text(
            p, height=3,
            font=("Courier",9), bg=BG3, fg=WHITE,
            insertbackground=WHITE, relief=tk.FLAT)
        self.zip_custom_txt.pack(fill=tk.X, padx=12, pady=(0,6))

        # buttons
        btn_row = tk.Frame(p, bg=BG)
        btn_row.pack(fill=tk.X, padx=12, pady=4)
        tk.Button(btn_row, text="BUILD ZIP",
                  font=("Courier",11,"bold"),
                  bg=BLOOD, fg=WHITE, relief=tk.FLAT,
                  pady=8, padx=16,
                  command=self._zip_build).pack(side=tk.LEFT)
        tk.Button(btn_row, text="build + sideload",
                  font=("Courier",10),
                  bg=ROYAL, fg=WHITE, relief=tk.FLAT,
                  pady=8, padx=12,
                  command=self._zip_build_and_flash).pack(side=tk.LEFT, padx=8)

        self.zip_out_lbl = tk.Label(
            p, text="", font=("Courier",9),
            bg=BG, fg=GREEN, wraplength=650, justify=tk.LEFT)
        self.zip_out_lbl.pack(anchor=tk.W, padx=12, pady=4)

    # ── UNPACK + EDIT TAB ─────────────────────────────────────────────────────

    def _build_ztab_unpack(self):
        p = self._ztab_unpack

        tk.Label(p, text="UNPACK + EDIT FIRMWARE",
                 font=("Courier",11,"bold"),
                 bg=BG, fg=BLOOD2).pack(anchor=tk.W, padx=12, pady=(10,4))

        tk.Label(p,
            text="unpack Samsung .tar.md5 firmware, edit FRP files, repack as sideload zip",
            font=("Courier",9,"italic"), bg=BG, fg=GREY
            ).pack(anchor=tk.W, padx=12, pady=(0,6))

        # source selector
        src_row = tk.Frame(p, bg=BG)
        src_row.pack(fill=tk.X, padx=12, pady=4)
        tk.Label(src_row, text="firmware file:",
                 font=("Courier",10), bg=BG, fg=GREY).pack(side=tk.LEFT)
        self.unpack_src = tk.StringVar(value="")
        tk.Entry(src_row, textvariable=self.unpack_src,
                 font=("Courier",9), bg=BG3, fg=GOLD,
                 insertbackground=WHITE, relief=tk.FLAT, width=36
                 ).pack(side=tk.LEFT, padx=6, ipady=3)
        tk.Button(src_row, text="browse",
                  font=("Courier",9), bg=BG3, fg=VIOLET,
                  relief=tk.FLAT,
                  command=self._unpack_browse).pack(side=tk.LEFT, padx=(0,4))
        tk.Button(src_row, text="use downloaded",
                  font=("Courier",9), bg=BG3, fg=VIOLET,
                  relief=tk.FLAT,
                  command=self._unpack_use_downloaded).pack(side=tk.LEFT)

        # output dir
        out_row = tk.Frame(p, bg=BG)
        out_row.pack(fill=tk.X, padx=12, pady=4)
        tk.Label(out_row, text="extract to:",
                 font=("Courier",10), bg=BG, fg=GREY).pack(side=tk.LEFT)
        unpack_default = os.path.join(
            os.environ.get("USERPROFILE", os.path.expanduser("~")),
            "Downloads", "soulworn_fw_extract")
        self.unpack_outdir = tk.StringVar(value=unpack_default)
        tk.Entry(out_row, textvariable=self.unpack_outdir,
                 font=("Courier",9), bg=BG3, fg=WHITE,
                 insertbackground=WHITE, relief=tk.FLAT, width=36
                 ).pack(side=tk.LEFT, padx=6, ipady=3)

        # edit actions
        edit_frame = tk.Frame(p, bg=BG3, padx=12, pady=8)
        edit_frame.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(edit_frame, text="EDIT ACTIONS after unpack:",
                 font=("Courier",10,"bold"),
                 bg=BG3, fg=VIOLET).pack(anchor=tk.W, pady=(0,6))

        self._edit_actions = {}
        edit_items = [
            ("zero_frp",      "Zero FRP partition files (FactoryApp/a,b)",     True),
            ("clear_flags",   "Clear FRP flags in build.prop",                  True),
            ("patch_settingsdb","Patch settings.db FRP entries",               True),
            ("zero_misc",     "Zero /misc partition FRP data",                  True),
            ("strip_google",  "Remove Google account binding files",            False),
            ("patch_csc",     "Patch CSC for region unlock",                    False),
            ("add_adb",       "Force enable ADB in build.prop",                 False),
            ("remove_knox",   "Remove Knox enforcement flags",                  False),
        ]
        for key, label, default in edit_items:
            var = tk.BooleanVar(value=default)
            self._edit_actions[key] = var
            tk.Checkbutton(edit_frame, text=label,
                           variable=var,
                           font=("Courier",9),
                           bg=BG3, fg=LAVENDER,
                           selectcolor=BG2,
                           activebackground=BG3
                           ).pack(anchor=tk.W, pady=1)

        # action buttons
        btn_row = tk.Frame(p, bg=BG)
        btn_row.pack(fill=tk.X, padx=12, pady=6)
        tk.Button(btn_row, text="UNPACK",
                  font=("Courier",10,"bold"),
                  bg=BG3, fg=VIOLET, relief=tk.FLAT,
                  pady=6, padx=12,
                  command=self._fw_unpack).pack(side=tk.LEFT, padx=(0,6))
        tk.Button(btn_row, text="APPLY EDITS",
                  font=("Courier",10,"bold"),
                  bg=ROYAL, fg=WHITE, relief=tk.FLAT,
                  pady=6, padx=12,
                  command=self._fw_apply_edits).pack(side=tk.LEFT, padx=(0,6))
        tk.Button(btn_row, text="REPACK TO ZIP",
                  font=("Courier",10,"bold"),
                  bg=BLOOD, fg=WHITE, relief=tk.FLAT,
                  pady=6, padx=12,
                  command=self._fw_repack).pack(side=tk.LEFT, padx=(0,6))
        tk.Button(btn_row, text="DO ALL THREE",
                  font=("Courier",11,"bold"),
                  bg=BLOOD2, fg=WHITE, relief=tk.FLAT,
                  pady=6, padx=12,
                  command=self._fw_do_all).pack(side=tk.LEFT)

        # log
        self.unpack_log = scrolledtext.ScrolledText(
            p, height=8,
            font=("Courier",9), bg="#020208", fg=GREEN,
            relief=tk.FLAT, state=tk.DISABLED,
        )
        self.unpack_log.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

    def _unpack_log_write(self, text):
        self.unpack_log.config(state=tk.NORMAL)
        self.unpack_log.insert(tk.END, text)
        self.unpack_log.see(tk.END)
        self.unpack_log.config(state=tk.DISABLED)

    def _unpack_browse(self):
        path = filedialog.askopenfilename(
            title="select Samsung firmware",
            filetypes=[
                ("Samsung firmware","*.zip *.tar *.md5"),
                ("All files","*.*"),
            ]
        )
        if path:
            self.unpack_src.set(path)
            self._fw_local_path = path

    def _unpack_use_downloaded(self):
        if self._fw_local_path:
            self.unpack_src.set(self._fw_local_path)
        else:
            self._ghost_say("no downloaded firmware yet -- use search tab first")

    def _fw_unpack(self):
        src     = self.unpack_src.get().strip()
        out_dir = self.unpack_outdir.get().strip()
        if not src or not os.path.exists(src):
            messagebox.showerror("unpack","select a valid firmware file first")
            return
        os.makedirs(out_dir, exist_ok=True)
        self._ghost_say("unpacking firmware...")
        self.root.after(0, lambda: self._unpack_log_write(
            f"unpacking: {src}\nto: {out_dir}\n\n"))

        def _run():
            try:
                import tarfile, zipfile as _zf

                self.root.after(0, lambda:
                    self._unpack_log_write("detecting format...\n"))

                if src.endswith(".zip"):
                    with _zf.ZipFile(src,"r") as zf:
                        names = zf.namelist()
                        self.root.after(0, lambda:
                            self._unpack_log_write(
                                f"ZIP: {len(names)} files\n"))
                        zf.extractall(out_dir)

                elif src.endswith(".tar") or src.endswith(".md5") \
                        or "tar" in src.lower():
                    # strip md5 suffix if needed -- Samsung .tar.md5
                    actual = src
                    if src.endswith(".md5"):
                        # Samsung tar.md5 -- just open as tar
                        pass
                    with tarfile.open(actual,"r:*") as tf:
                        members = tf.getmembers()
                        self.root.after(0, lambda:
                            self._unpack_log_write(
                                f"TAR: {len(members)} members\n"))
                        tf.extractall(out_dir)

                        # look for inner AP file (main system)
                        for m in members:
                            if m.name.startswith("AP_") and \
                                    m.name.endswith(".tar.md5"):
                                ap_path = os.path.join(out_dir, m.name)
                                self.root.after(0, lambda:
                                    self._unpack_log_write(
                                        f"found AP file: {m.name}\n"
                                        f"extracting AP...\n"))
                                try:
                                    with tarfile.open(ap_path,"r:*") as apf:
                                        apf.extractall(
                                            os.path.join(out_dir,"ap_extracted"))
                                    self.root.after(0, lambda:
                                        self._unpack_log_write("AP extracted\n"))
                                except Exception as ae:
                                    self.root.after(0, lambda:
                                        self._unpack_log_write(
                                            f"AP extract warning: {ae}\n"))

                self._fw_unpacked = out_dir
                self.root.after(0, lambda:
                    self._unpack_log_write(
                        f"\nunpack complete: {out_dir}\n"
                        f"now tap APPLY EDITS to patch FRP files\n"))
                self.root.after(0, lambda:
                    self._ghost_say("firmware unpacked -- apply edits next"))

            except Exception as e:
                self.root.after(0, lambda:
                    self._unpack_log_write(f"unpack error: {e}\n"))
                self.root.after(0, lambda:
                    self._ghost_say(f"unpack failed: {e}"))

        threading.Thread(target=_run, daemon=True).start()

    def _fw_apply_edits(self):
        out_dir = self._fw_unpacked or self.unpack_outdir.get().strip()
        if not out_dir or not os.path.isdir(out_dir):
            messagebox.showerror("edit","unpack firmware first")
            return

        actions = {k: v.get() for k,v in self._edit_actions.items()}
        self._ghost_say("applying FRP edits to firmware files...")
        self.root.after(0, lambda:
            self._unpack_log_write(f"\napplying edits to: {out_dir}\n"))

        def _run():
            edits = 0

            # walk directory tree looking for target files
            for root_dir, dirs, files in os.walk(out_dir):
                for fname in files:
                    full = os.path.join(root_dir, fname)

                    # build.prop edits
                    if fname == "build.prop" and actions.get("clear_flags"):
                        try:
                            with open(full,"r",errors="ignore") as f:
                                content = f.read()
                            orig = content

                            # FRP disablement props
                            frp_props = {
                                "ro.frp.pst":          "",
                                "persist.security.frp.lock": "0",
                                "ro.setupwizard.mode": "DISABLED",
                            }
                            for prop, val in frp_props.items():
                                if prop in content:
                                    import re as _re
                                    content = _re.sub(
                                        rf"^{prop}=.*$", f"{prop}={val}",
                                        content, flags=_re.MULTILINE)

                            if actions.get("add_adb"):
                                if "ro.adb.secure" not in content:
                                    content += "\nro.adb.secure=0\n"
                                content = content.replace(
                                    "ro.adb.secure=1","ro.adb.secure=0")

                            if actions.get("remove_knox"):
                                knox_props = [
                                    "ro.knox","sec.knox",
                                    "ro.build.knox","ro.enterprise.mdm",
                                ]
                                for kp in knox_props:
                                    content = content.replace(
                                        f"{kp}=1", f"{kp}=0")

                            if content != orig:
                                with open(full,"w") as f:
                                    f.write(content)
                                self.root.after(0, lambda fp=full:
                                    self._unpack_log_write(
                                        f"  patched: {fp}\n"))
                                edits += 1
                        except Exception as e:
                            self.root.after(0, lambda:
                                self._unpack_log_write(
                                    f"  build.prop error: {e}\n"))

                    # FRP account files
                    if actions.get("zero_frp") and fname in ("a","b","keydata"):
                        if "FactoryApp" in root_dir or "Factory" in root_dir:
                            try:
                                with open(full,"w") as f:
                                    f.write("")
                                self.root.after(0, lambda fp=full:
                                    self._unpack_log_write(
                                        f"  zeroed: {fp}\n"))
                                edits += 1
                            except Exception:
                                pass

                    # settings.db
                    if actions.get("patch_settingsdb") and \
                            fname == "settings.db":
                        try:
                            import sqlite3 as _sql
                            conn = _sql.connect(full)
                            cur  = conn.cursor()
                            for tbl in ("secure","global"):
                                try:
                                    cur.execute(
                                        f"INSERT OR REPLACE INTO {tbl}"
                                        f"(name,value) VALUES"
                                        f"('user_setup_complete','1')")
                                    cur.execute(
                                        f"INSERT OR REPLACE INTO {tbl}"
                                        f"(name,value) VALUES"
                                        f"('device_provisioned','1')")
                                except Exception:
                                    pass
                            conn.commit()
                            conn.close()
                            self.root.after(0, lambda fp=full:
                                self._unpack_log_write(
                                    f"  patched settings.db: {fp}\n"))
                            edits += 1
                        except Exception as e:
                            self.root.after(0, lambda:
                                self._unpack_log_write(
                                    f"  settings.db error: {e}\n"))

            self.root.after(0, lambda:
                self._unpack_log_write(
                    f"\nedits applied: {edits} files modified\n"
                    f"now tap REPACK TO ZIP\n"))
            self.root.after(0, lambda:
                self._ghost_say(f"{edits} files patched -- repack next"))

        threading.Thread(target=_run, daemon=True).start()

    def _fw_repack(self):
        out_dir = self._fw_unpacked or self.unpack_outdir.get().strip()
        if not out_dir or not os.path.isdir(out_dir):
            messagebox.showerror("repack","apply edits first")
            return

        model = self._zip_vars.get("zip_model",
                tk.StringVar(value="device")).get() if self._zip_vars else "device"
        safe  = re.sub(r"[^\w\-]","_", model)
        dl_dir = os.path.join(
            os.environ.get("USERPROFILE", os.path.expanduser("~")),
            "Downloads")
        zip_path = os.path.join(dl_dir, f"soulworn_edited_{safe}.zip")

        self._ghost_say("repacking firmware files into sideload zip...")
        self.root.after(0, lambda:
            self._unpack_log_write(f"\nrepacking to: {zip_path}\n"))

        def _run():
            try:
                import zipfile as _zf

                # build update-binary that applies the edited files
                binary = (
                    "#!/sbin/sh\n"
                    "OUTFD=$2\n"
                    'ui_print() { echo "ui_print $1" >> /proc/self/fd/$OUTFD;'
                    ' echo "ui_print " >> /proc/self/fd/$OUTFD; }\n'
                    'set_progress() { echo "set_progress $1" >> /proc/self/fd/$OUTFD; }\n'
                    'ui_print "=============================="\n'
                    f'ui_print "  SoulWoRn Edited Firmware"\n'
                    f'ui_print "  {model}"\n'
                    'ui_print "=============================="\n'
                    "set_progress 0.1\n"
                    "mount /system 2>/dev/null || mount -o rw /system 2>/dev/null\n"
                    "mount /data   2>/dev/null\n"
                    "set_progress 0.3\n"
                )

                with _zf.ZipFile(zip_path,"w",_zf.ZIP_DEFLATED) as zf:
                    # write update-binary
                    info_z = _zf.ZipInfo(
                        "META-INF/com/google/android/update-binary")
                    info_z.external_attr = 0o755 << 16

                    # walk edited dir and add all files + install cmds
                    install_cmds = ""
                    file_count   = 0
                    for root_dir, dirs, files in os.walk(out_dir):
                        for fname in files:
                            full     = os.path.join(root_dir, fname)
                            rel_path = os.path.relpath(full, out_dir)
                            arc_path = f"system_files/{rel_path}"
                            try:
                                zf.write(full, arc_path)
                                # add install command
                                if fname == "build.prop":
                                    dest = f"/system/{rel_path}"
                                    install_cmds += (
                                        f'package_extract_file "{arc_path}"'
                                        f' "{dest}"\n'
                                        f'set_perm 0 0 0644 "{dest}"\n'
                                    )
                                file_count += 1
                            except Exception:
                                pass

                    full_binary = (binary + install_cmds +
                                   "set_progress 1.0\n"
                                   'ui_print "DONE -- Reboot now"\n')
                    zf.writestr(info_z, full_binary)
                    zf.writestr(
                        "META-INF/com/google/android/updater-script",
                        f'ui_print("SoulWoRn edited -- {model}");')

                size = os.path.getsize(zip_path)
                md5  = hashlib.md5(open(zip_path,"rb").read()).hexdigest()
                self.root.after(0, lambda:
                    self._unpack_log_write(
                        f"repacked: {zip_path}\n"
                        f"files: {file_count}  size: {size//1024}KB\n"
                        f"MD5: {md5}\n"
                        f"sideload: adb sideload {zip_path}\n"))
                self.root.after(0, lambda:
                    self._ghost_say(f"zip ready: {os.path.basename(zip_path)}"))
                audit_log("FW_REPACK", f"{model} -> {zip_path}")

            except Exception as e:
                self.root.after(0, lambda:
                    self._unpack_log_write(f"repack error: {e}\n"))

        threading.Thread(target=_run, daemon=True).start()

    def _fw_do_all(self):
        """Unpack → edit → repack in sequence."""
        def _chain():
            self._fw_unpack()
            # wait for unpack to finish
            self.root.after(8000, self._fw_apply_edits)
            self.root.after(16000, self._fw_repack)
        threading.Thread(target=_chain, daemon=True).start()
        self._ghost_say("running: unpack > edit > repack -- watch the log!!")



    def _zip_autofill(self):
        serial = self._get_serial()
        if not serial:
            self._ghost_say("connect device first")
            return
        info = get_device_info(serial)
        self._zip_vars["zip_model"].set(info.get("Model","Unknown"))
        self._zip_vars["zip_codename"].set(info.get("Codename","generic"))
        self._zip_vars["zip_android"].set(info.get("Android","?"))
        self._zip_vars["zip_patch"].set(info.get("Patch","?"))
        model = info.get("Model","device")
        safe  = re.sub(r"[^\w\-]","_", model)
        self._zip_vars["zip_fname"].set(f"soulworn_frp_{safe}.zip")
        self.zip_status.config(text=f"filled from {model}")
        self._ghost_say(f"zip config loaded from {model}")

    def _zip_build(self, then_flash=False):
        import zipfile as _zf
        model    = self._zip_vars["zip_model"].get()
        codename = self._zip_vars["zip_codename"].get()
        android  = self._zip_vars["zip_android"].get()
        patch    = self._zip_vars["zip_patch"].get()
        fname    = self._zip_vars["zip_fname"].get()
        ztype    = self.zip_type.get()
        custom   = self.zip_custom_txt.get("1.0", tk.END).strip()

        # determine output path
        dl_dir = os.path.join(
            os.environ.get("USERPROFILE", os.path.expanduser("~")),
            "Downloads")
        if not os.path.exists(dl_dir):
            dl_dir = os.path.expanduser("~")
        zip_path = os.path.join(dl_dir, fname)

        # build update-binary script
        frp_wipe = ztype in ("frp_full","frp_efs")
        efs_wipe = ztype in ("frp_efs","efs_only")
        flags    = ztype != "efs_only"
        custom_cmds = "\n".join(custom.splitlines()) if ztype == "custom" else ""

        efs_block = ""
        if efs_wipe:
            efs_paths = [
                "/efs/Factory/a","/efs/FactoryApp/a","/efs/FactoryApp/b",
                "/mnt/vendor/efs/FactoryApp/a","/mnt/vendor/efs/FactoryApp/b",
            ]
            efs_block = "\n".join([
                f'[ -e "{p}" ] && echo "" > "{p}" && ui_print "wiped: {p}"'
                for p in efs_paths
            ])

        # build flags commands separately to avoid f-string conflict
        if flags:
            flags_cmds = (
                "  sqlite3 $DB \"INSERT OR REPLACE INTO secure"
                "(name,value) VALUES('user_setup_complete','1');\" 2>/dev/null\n"
                "  sqlite3 $DB \"INSERT OR REPLACE INTO global"
                "(name,value) VALUES('device_provisioned','1');\""
                " 2>/dev/null"
            )
        else:
            flags_cmds = ""

        binary = (
            "#!/sbin/sh\n"
            f"# SoulWoRn Sideload ZIP\n"
            f"# {model} / {codename} / Android {android} / Patch {patch}\n"
            "OUTFD=$2\n"
            "ui_print() { echo \"ui_print $1\" >> /proc/self/fd/$OUTFD;"
            " echo \"ui_print \" >> /proc/self/fd/$OUTFD; }\n"
            "set_progress() { echo \"set_progress $1\" >> /proc/self/fd/$OUTFD; }\n"
            "ui_print \"=============================="
            "\"\nui_print \"  SoulWoRn FRP Clear\"\n"
            f"ui_print \"  {model} / {codename}\"\n"
            f"ui_print \"  Android {android}\"\n"
            "ui_print \"=============================="
            "\"\nset_progress 0.1\n"
            + (
                "FRP=\"\"\n"
                "for c in /dev/block/by-name/frp"
                " /dev/block/bootdevice/by-name/frp; do\n"
                "  [ -e \"$c\" ] && FRP=\"$c\" && break\ndone\n"
                "[ -z \"$FRP\" ] && FRP=$(find /dev/block/platform"
                " -name frp 2>/dev/null | head -1)\n"
                "[ -n \"$FRP\" ] && dd if=/dev/zero of=\"$FRP\""
                " bs=512 count=256 2>/dev/null"
                " && ui_print \"FRP partition zeroed\"\n"
                if frp_wipe else ""
            )
            + "set_progress 0.4\n"
            "mount /data 2>/dev/null\n"
            "if mount | grep -q \" /data \"; then\n"
            "  DB=\"/data/data/com.google.android.providers"
            ".settings/databases/settings.db\"\n"
            + flags_cmds + "\n"
            "  for f in /data/system/users/0/settings_secure.xml; do\n"
            "    [ -f \"$f\" ] && sed -i"
            " 's/frp_credential_enabled\" value=\"1\"/frp_credential_enabled"
            "\" value=\"0\"/g' \"$f\" 2>/dev/null\n"
            "  done\n"
            "  ui_print \"setup flags written\"\nfi\n"
            "set_progress 0.7\n"
            + efs_block + "\n"
            + custom_cmds + "\n"
            "set_progress 1.0\n"
            "ui_print \"=============================="
            "\"\nui_print \"  DONE -- Reboot system now\"\n"
            "ui_print \"=============================="
            "\"\n"
        )

        try:
            with _zf.ZipFile(zip_path, "w", _zf.ZIP_DEFLATED) as zf:
                info_z = _zf.ZipInfo("META-INF/com/google/android/update-binary")
                info_z.external_attr = 0o755 << 16
                zf.writestr(info_z, binary)
                zf.writestr(
                    "META-INF/com/google/android/updater-script",
                    f'ui_print("SoulWoRn -- {model}");')

            md5  = hashlib.md5(open(zip_path,"rb").read()).hexdigest()
            size = os.path.getsize(zip_path)
            msg  = (f"built: {zip_path}\n"
                    f"size: {size:,} bytes  |  MD5: {md5}\n"
                    f"sideload: adb sideload {zip_path}")
            self.zip_out_lbl.config(text=msg)
            self._log(f"zip built: {zip_path} ({size:,}b)")
            self._ghost_say(f"zip ready: {fname}")
            audit_log("ZIP_BUILD", f"{model} {ztype} {zip_path}")

            if then_flash:
                self._zip_sideload(zip_path)

        except Exception as e:
            self.zip_out_lbl.config(text=f"build failed: {e}", fg=BLOOD)
            self._log(f"zip build error: {e}")

    def _zip_build_and_flash(self):
        self._zip_build(then_flash=True)

    def _zip_sideload(self, zip_path):
        if not messagebox.askyesno("sideload",
                f"sideload {os.path.basename(zip_path)}?\n\n"
                "make sure device is in recovery >\n"
                "'Apply update from ADB' first"):
            return
        self._log(f"sideloading: {zip_path}")
        self._ghost_say("sideloading zip -- watch device screen...")
        def _run():
            code, out, err = adb("sideload", zip_path, timeout=120)
            self._log(f"sideload: {out or err}")
            self._ghost_say(f"sideload {'done' if code==0 else 'failed'}: {(out or err)[:60]}")
        threading.Thread(target=_run, daemon=True).start()

    # ----------------------------------------------------------
    # USB MONITOR / ARBITRATION TAB
    # ----------------------------------------------------------

    def _build_usb_tab(self):
        tk.Label(self.tab_usb,
                 text="USB MONITOR  --  device arbitration",
                 font=("Courier",11,"bold"),
                 bg=BG, fg=BLOOD2).pack(anchor=tk.W, padx=12, pady=(10,4))

        # status + control
        ctrl = tk.Frame(self.tab_usb, bg=BG)
        ctrl.pack(fill=tk.X, padx=12, pady=(0,6))

        self.usb_mon_active = tk.BooleanVar(value=False)
        self.usb_mon_btn = tk.Button(
            ctrl, text="START MONITORING",
            font=("Courier",10,"bold"),
            bg=BLOOD, fg=WHITE, relief=tk.FLAT,
            pady=6, padx=12,
            command=self._usb_toggle_monitor)
        self.usb_mon_btn.pack(side=tk.LEFT)

        self.usb_status_lbl = tk.Label(
            ctrl, text="  monitoring: off",
            font=("Courier",9), bg=BG, fg=GREY)
        self.usb_status_lbl.pack(side=tk.LEFT, padx=8)

        # preferences
        pref_frame = tk.Frame(self.tab_usb, bg=BG3, padx=12, pady=8)
        pref_frame.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(pref_frame, text="WHEN DEVICE CONNECTS:",
                 font=("Courier",10,"bold"),
                 bg=BG3, fg=VIOLET).pack(anchor=tk.W)

        self.usb_action = tk.StringVar(value="ask")
        actions = [
            ("Ask me every time",       "ask"),
            ("Auto-select SoulWoRn",    "soulworn"),
            ("Auto-launch BugJaeger",   "bugjaeger"),
            ("Silent -- just log",      "silent"),
        ]
        for label, val in actions:
            tk.Radiobutton(
                pref_frame, text=label,
                variable=self.usb_action, value=val,
                font=("Courier",9),
                bg=BG3, fg=LAVENDER,
                selectcolor=BG2,
                activebackground=BG3).pack(anchor=tk.W, pady=2)

        # known devices pref
        tk.Label(pref_frame,
                 text="\nremember per vendor:product ID (saved to ~/.nkit_usb_prefs.json)",
                 font=("Courier",8,"italic"),
                 bg=BG3, fg=GREY).pack(anchor=tk.W)

        # event log
        tk.Label(self.tab_usb, text="USB events:",
                 font=("Courier",10,"bold"),
                 bg=BG, fg=BLOOD2).pack(anchor=tk.W, padx=12, pady=(8,2))

        self.usb_log = scrolledtext.ScrolledText(
            self.tab_usb, height=12,
            font=("Courier",9),
            bg="#020208", fg=GREEN,
            relief=tk.FLAT, state=tk.DISABLED,
        )
        self.usb_log.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        self.usb_log.tag_config("connect",    foreground=GREEN)
        self.usb_log.tag_config("disconnect", foreground=BLOOD)
        self.usb_log.tag_config("info",       foreground=VIOLET)

        # current devices
        refresh_row = tk.Frame(self.tab_usb, bg=BG)
        refresh_row.pack(fill=tk.X, padx=12, pady=4)
        tk.Button(refresh_row, text="scan now",
                  font=("Courier",9), bg=BG3, fg=VIOLET,
                  relief=tk.FLAT, padx=8,
                  command=self._usb_scan_now).pack(side=tk.LEFT)
        tk.Button(refresh_row, text="clear log",
                  font=("Courier",9), bg=BG3, fg=GREY,
                  relief=tk.FLAT, padx=8,
                  command=self._usb_clear_log).pack(side=tk.LEFT, padx=4)

        # internal state
        self._usb_prev_devices  = set()
        self._usb_monitor_thread= None
        self._usb_stop_event    = threading.Event()
        self._usb_prefs_file    = os.path.expanduser("~/.nkit_usb_prefs.json")
        self._usb_prefs         = self._load_usb_prefs()

        # android vendor IDs
        self._android_vendors = {
            "04e8":"Samsung",  "18d1":"Google",   "2a70":"OnePlus",
            "2717":"Xiaomi",   "12d1":"Huawei",   "1004":"LG",
            "0fce":"Sony",     "22b8":"Motorola", "0bb4":"HTC",
            "0502":"Acer",     "2970":"Maxwest",  "19d2":"ZTE",
        }

        self._usb_log_write("USB monitor ready -- tap START MONITORING\n", "info")

    def _usb_log_write(self, text, tag="info"):
        self.usb_log.config(state=tk.NORMAL)
        ts = time.strftime("%H:%M:%S")
        self.usb_log.insert(tk.END, f"[{ts}] {text}", tag)
        self.usb_log.see(tk.END)
        self.usb_log.config(state=tk.DISABLED)

    def _load_usb_prefs(self):
        try:
            if os.path.exists(self._usb_prefs_file):
                with open(self._usb_prefs_file) as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_usb_prefs(self):
        try:
            with open(self._usb_prefs_file, "w") as f:
                json.dump(self._usb_prefs, f, indent=2)
        except Exception:
            pass

    def _usb_scan_now(self):
        devs = get_devices()
        self._usb_log_write(f"adb scan: {len(devs)} device(s)\n", "info")
        for d in devs:
            self._usb_log_write(
                f"  {d['serial']}  [{d['state']}]\n", "connect")
        if not devs:
            self._usb_log_write("  no devices\n", "info")

    def _usb_clear_log(self):
        self.usb_log.config(state=tk.NORMAL)
        self.usb_log.delete("1.0", tk.END)
        self.usb_log.config(state=tk.DISABLED)

    def _usb_toggle_monitor(self):
        if self.usb_mon_active.get():
            # stop
            self._usb_stop_event.set()
            self.usb_mon_active.set(False)
            self.usb_mon_btn.config(
                text="START MONITORING", bg=BLOOD)
            self.usb_status_lbl.config(
                text="  monitoring: off", fg=GREY)
            self._usb_log_write("monitor stopped\n", "info")
        else:
            # start
            self._usb_stop_event.clear()
            self.usb_mon_active.set(True)
            self.usb_mon_btn.config(
                text="STOP MONITORING", bg=BG3)
            self.usb_status_lbl.config(
                text="  monitoring: ON -- polling every 2s",
                fg=GREEN)
            self._usb_log_write("monitor started -- polling adb devices\n", "info")
            self._usb_prev_devices = set(
                d["serial"] for d in get_devices())
            t = threading.Thread(
                target=self._usb_monitor_loop, daemon=True)
            self._usb_monitor_thread = t
            t.start()

    def _usb_monitor_loop(self):
        """Poll adb devices every 2s, detect changes, fire arbitration dialog."""
        while not self._usb_stop_event.is_set():
            try:
                current_devs = get_devices()
                current_set  = set(d["serial"] for d in current_devs)
                prev_set     = self._usb_prev_devices

                # new connections
                for serial in current_set - prev_set:
                    dev = next((d for d in current_devs
                                if d["serial"] == serial), {})
                    self.root.after(0, lambda s=serial, d=dev:
                        self._usb_on_connect(s, d))

                # disconnections
                for serial in prev_set - current_set:
                    self.root.after(0, lambda s=serial:
                        self._usb_on_disconnect(s))

                self._usb_prev_devices = current_set

            except Exception as e:
                self.root.after(0, lambda err=e:
                    self._usb_log_write(f"monitor error: {err}\n", "info"))

            self._usb_stop_event.wait(2)

    def _usb_on_connect(self, serial, dev):
        state = dev.get("state","device")
        # try to get vendor info
        _, out, _ = adb("-s", serial, "shell",
                        "getprop ro.product.brand 2>/dev/null")
        brand = out.strip() or "unknown"
        _, model_out, _ = adb("-s", serial, "shell",
                               "getprop ro.product.model 2>/dev/null")
        model = model_out.strip() or serial

        self._usb_log_write(
            f"CONNECTED: {serial} | {brand} {model} | [{state}]\n",
            "connect")
        self._log(f"USB: {brand} {model} connected")
        self._ghost_say(f"device connected: {brand} {model}")
        audit_log("USB_CONNECT", f"{brand} {model}", serial)

        # arbitration
        action = self.usb_action.get()
        pref   = self._usb_prefs.get(serial)

        if pref:
            action = pref
            self._usb_log_write(
                f"  using saved preference: {pref}\n", "info")

        if action == "ask" or (not pref and action == "ask"):
            self._usb_arbitration_dialog(serial, brand, model)
        elif action == "soulworn":
            # auto-select in SoulWoRn
            self.serial.set(serial)
            self.dev_info_lbl.config(
                text=f"{brand} {model}", fg=GOLD)
            self._usb_log_write(
                f"  auto-selected in SoulWoRn\n", "info")
        elif action == "bugjaeger":
            self._usb_launch_bugjaeger()
        # silent = just log, already done

    def _usb_on_disconnect(self, serial):
        self._usb_log_write(
            f"DISCONNECTED: {serial}\n", "disconnect")
        self._log(f"USB: {serial} disconnected")
        audit_log("USB_DISCONNECT", serial)

    def _usb_arbitration_dialog(self, serial, brand, model):
        """Popup dialog -- choose what to do with newly connected device."""
        win = tk.Toplevel(self.root)
        win.title("USB Device Connected")
        win.geometry("420x340")
        win.configure(bg=BG)
        win.lift()
        win.focus_force()

        tk.Label(win, text="USB DEVICE CONNECTED",
                 font=("Courier",12,"bold"),
                 bg=BG, fg=BLOOD2).pack(pady=(16,4))
        tk.Label(win,
                 text=f"{brand}  {model}\n{serial}",
                 font=("Courier",10),
                 bg=BG, fg=GOLD).pack(pady=4)

        tk.Label(win, text="open with:",
                 font=("Courier",10), bg=BG, fg=GREY).pack(pady=(12,4))

        def _choose(action, remember=False):
            if remember:
                self._usb_prefs[serial] = action
                self._save_usb_prefs()
                self._usb_log_write(
                    f"  preference saved: {action} for {serial}\n", "info")
            if action == "soulworn":
                self.serial.set(serial)
                self.dev_info_lbl.config(
                    text=f"{brand} {model}", fg=GOLD)
                self._usb_log_write(
                    f"  opened in SoulWoRn\n", "info")
                self._ghost_say(
                    f"got it -- {brand} {model} selected in SoulWoRn")
                self.tabs.select(0)  # switch to FRP tab
            elif action == "bugjaeger":
                self._usb_launch_bugjaeger()
            elif action == "frp":
                self.serial.set(serial)
                self._run_frp("1")
            win.destroy()

        btns = [
            ("Open in SoulWoRn",       lambda: _choose("soulworn"),  BLOOD),
            ("Run FRP bypass now",      lambda: _choose("frp"),       ROYAL),
            ("Launch BugJaeger",        lambda: _choose("bugjaeger"), BG3),
            ("Ignore",                  lambda: win.destroy(),        BG3),
        ]
        for label, cmd, color in btns:
            tk.Button(win, text=label,
                      font=("Courier",10),
                      bg=color, fg=WHITE, relief=tk.FLAT,
                      pady=8, width=28,
                      command=cmd).pack(pady=3)

        # remember checkbox
        remember_var = tk.BooleanVar(value=False)
        tk.Checkbutton(win,
                       text="remember for this device",
                       variable=remember_var,
                       font=("Courier",9),
                       bg=BG, fg=GREY,
                       selectcolor=BG3,
                       activebackground=BG).pack(pady=(8,4))

        # override choose to use remember_var
        for i, (label, _, color) in enumerate(btns[:-1]):
            action_map = ["soulworn","frp","bugjaeger"]
            if i < len(action_map):
                btn_action = action_map[i]
                # find and rebind button
                for widget in win.winfo_children():
                    if isinstance(widget, tk.Button) and widget.cget("text") == label:
                        widget.config(command=lambda a=btn_action:
                            _choose(a, remember_var.get()))

    def _usb_launch_bugjaeger(self):
        """Try to launch BugJaeger if on Android via am start."""
        self._usb_log_write("attempting BugJaeger launch...\n", "info")
        code, out, err = adb("shell",
            "am start -n eu.sisik.hackendebug/.MainActivity 2>/dev/null")
        if code == 0:
            self._usb_log_write("BugJaeger launched\n", "connect")
        else:
            self._usb_log_write(
                "BugJaeger not found on host device\n", "info")
            self._log("BugJaeger launch failed -- not installed")

    def _build_ai_tab(self):
        tk.Label(self.tab_ai,
                 text="Ghosteey AI  --  Claude / Groq / Ollama / Offline",
                 font=("Courier", 11, "bold"),
                 bg=BG, fg=BLOOD2).pack(anchor=tk.W, padx=12, pady=(10, 4))

        # status bar
        self.ai_status_var = tk.StringVar(value="checking AI status...")
        tk.Label(self.tab_ai, textvariable=self.ai_status_var,
                 font=("Courier", 9), bg=BG, fg=GOLD).pack(
                     anchor=tk.W, padx=12, pady=(0, 6))
        self._update_ai_status()

        # chat log
        self.chat_log = scrolledtext.ScrolledText(
            self.tab_ai, font=("Courier", 10),
            bg="#05050a", fg=LAVENDER,
            insertbackground=LAVENDER,
            relief=tk.FLAT, wrap=tk.WORD,
            state=tk.DISABLED, height=16,
        )
        self.chat_log.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # colour tags
        self.chat_log.tag_config("user",    foreground=BLOOD2)
        self.chat_log.tag_config("ghost",   foreground=VIOLET)
        self.chat_log.tag_config("source",  foreground=GREY)
        self.chat_log.tag_config("code",    foreground=GOLD)
        self.chat_log.tag_config("reply",   foreground=LAVENDER)

        # input row
        input_row = tk.Frame(self.tab_ai, bg=BG)
        input_row.pack(fill=tk.X, padx=8, pady=(0, 6))

        self.ai_input = tk.Entry(input_row, font=("Courier", 11),
                                  bg=BG3, fg=WHITE, insertbackground=WHITE,
                                  relief=tk.FLAT)
        self.ai_input.pack(side=tk.LEFT, fill=tk.X, expand=True,
                            padx=(0, 6), ipady=6)
        self.ai_input.bind("<Return>", lambda e: self._send_ai())

        tk.Button(input_row, text="send",
                  font=("Courier", 10, "bold"),
                  bg=BLOOD, fg=WHITE, relief=tk.FLAT,
                  width=7, pady=4,
                  activebackground=BLOOD2,
                  command=self._send_ai).pack(side=tk.LEFT)

        tk.Button(input_row, text="clear",
                  font=("Courier", 10),
                  bg=BG3, fg=GREY, relief=tk.FLAT,
                  width=6, pady=4,
                  command=self._clear_chat).pack(side=tk.LEFT, padx=4)

    # ----------------------------------------------------------
    # SETTINGS TAB
    # ----------------------------------------------------------

    def _build_settings_tab(self):
        tk.Label(self.tab_settings, text="SETTINGS  --  API keys + config",
                 font=("Courier", 11, "bold"),
                 bg=BG, fg=BLOOD2).pack(anchor=tk.W, padx=12, pady=(10, 8))

        # Claude key
        self._key_row(self.tab_settings,
                      "Claude API key  (console.anthropic.com)",
                      KEY_FILE, "sk-ant-")

        # Groq key
        self._key_row(self.tab_settings,
                      "Groq API key  (console.groq.com -- FREE)",
                      GROQ_KEY_FILE, "gsk_")

        tk.Label(self.tab_settings,
                 text="\n  AI fallback order:\n"
                      "  1. Claude  (if key set)\n"
                      "  2. Groq  (if key set -- free tier available)\n"
                      "  3. Ollama  (if running locally on this machine)\n"
                      "  4. Offline canned responses  (always works)\n",
                 font=("Courier", 10), bg=BG, fg=GREY,
                 justify=tk.LEFT).pack(anchor=tk.W, padx=12)

        # ADB path -- auto-discovery + browse
        tk.Label(self.tab_settings, text="  ADB / Platform-Tools:",
                 font=("Courier", 10, "bold"),
                 bg=BG, fg=VIOLET).pack(anchor=tk.W, padx=12, pady=(8, 2))

        adb_frame = tk.Frame(self.tab_settings, bg=BG3, pady=8, padx=12)
        adb_frame.pack(fill=tk.X, padx=8, pady=3)

        self.adb_path_var = tk.StringVar(value=ADB_PATH)
        adb_found = ADB_PATH != "adb" and os.path.isfile(ADB_PATH)
        adb_color = GREEN if adb_found else BLOOD2
        status_text = "found:" if adb_found else "NOT found -- browse or download platform-tools:"

        tk.Label(adb_frame, text=status_text,
                 font=("Courier", 9), bg=BG3,
                 fg=adb_color).pack(anchor=tk.W)

        adb_row = tk.Frame(adb_frame, bg=BG3)
        adb_row.pack(fill=tk.X, pady=(4, 0))

        self.adb_entry = tk.Entry(adb_row, textvariable=self.adb_path_var,
                                   font=("Courier", 9),
                                   bg=BG2, fg=GREEN if adb_found else GREY,
                                   insertbackground=WHITE,
                                   relief=tk.FLAT, width=48)
        self.adb_entry.pack(side=tk.LEFT, padx=(0, 6), ipady=3)

        def browse_adb():
            path = filedialog.askopenfilename(
                title="locate adb.exe",
                filetypes=[
                    ("ADB executable", "adb.exe adb"),
                    ("All files", "*.*"),
                ],
                initialdir=os.environ.get("USERPROFILE",
                           os.path.expanduser("~")),
            )
            if path:
                self.adb_path_var.set(path)
                _save_adb_path(path)
                self.adb_entry.config(fg=GREEN)
                self._log(f"adb path set: {path}")
                self._ghost_say(f"adb locked and loaded: {os.path.basename(path)}")

        def rescan_adb():
            found = _find_adb()
            self.adb_path_var.set(found)
            _save_adb_path(found)
            color = GREEN if (found != "adb" and os.path.isfile(found)) else BLOOD2
            self.adb_entry.config(fg=color)
            self._log(f"adb scan result: {found}")
            self._ghost_say(f"adb {'found' if color == GREEN else 'not found'}: {found}")

        def save_adb():
            path = self.adb_path_var.get().strip()
            if path and (os.path.isfile(path) or path == "adb"):
                _save_adb_path(path)
                self._log(f"adb path saved: {path}")
                self._ghost_say("adb path saved")
            else:
                messagebox.showerror("error", f"file not found: {path}")

        tk.Button(adb_row, text="browse",
                  font=("Courier", 9), bg=ROYAL, fg=WHITE,
                  relief=tk.FLAT, pady=2, width=7,
                  command=browse_adb).pack(side=tk.LEFT, padx=(0, 4))

        tk.Button(adb_row, text="rescan",
                  font=("Courier", 9), bg=BG2, fg=VIOLET,
                  relief=tk.FLAT, pady=2, width=7,
                  command=rescan_adb).pack(side=tk.LEFT, padx=(0, 4))

        tk.Button(adb_row, text="save",
                  font=("Courier", 9), bg=BG2, fg=GREY,
                  relief=tk.FLAT, pady=2, width=6,
                  command=save_adb).pack(side=tk.LEFT)

        tk.Label(adb_frame,
                 text="download platform-tools: developer.android.com/tools/releases/platform-tools",
                 font=("Courier", 8), bg=BG3, fg=GREY).pack(anchor=tk.W, pady=(4, 0))

    def _key_row(self, parent, label, keyfile, prefix):
        frame = tk.Frame(parent, bg=BG3, pady=8, padx=12)
        frame.pack(fill=tk.X, padx=8, pady=3)

        tk.Label(frame, text=label, font=("Courier", 10),
                 bg=BG3, fg=WHITE).pack(anchor=tk.W)

        row = tk.Frame(frame, bg=BG3)
        row.pack(fill=tk.X, pady=(4, 0))

        existing = _load_key(keyfile)
        placeholder = f"set ({existing[:14]}...)" if existing else f"paste {prefix}..."

        entry = tk.Entry(row, font=("Courier", 10),
                          bg=BG2, fg=GOLD if existing else GREY,
                          insertbackground=WHITE, relief=tk.FLAT, width=44,
                          show="*")
        if existing:
            entry.insert(0, existing)
        else:
            entry.insert(0, placeholder)
        entry.pack(side=tk.LEFT, padx=(0, 8), ipady=4)

        def save_key(e=entry, f=keyfile, p=prefix):
            val = e.get().strip()
            if val and val.startswith(p):
                _save_key(f, val)
                self._log(f"key saved to {f}")
                self._update_ai_status()
                messagebox.showinfo("saved", "API key saved!")
            else:
                messagebox.showerror("error", f"key should start with {p}")

        tk.Button(row, text="save",
                  font=("Courier", 10),
                  bg=ROYAL, fg=WHITE, relief=tk.FLAT,
                  width=6, pady=2,
                  command=save_key).pack(side=tk.LEFT)

        def clear_key(f=keyfile, e=entry):
            if os.path.exists(f):
                os.remove(f)
            e.delete(0, tk.END)
            self._update_ai_status()
            self._log(f"key cleared: {f}")

        tk.Button(row, text="clear",
                  font=("Courier", 10),
                  bg=BG2, fg=GREY, relief=tk.FLAT,
                  width=6, pady=2,
                  command=clear_key).pack(side=tk.LEFT, padx=4)

    # ----------------------------------------------------------
    # DEVICE HELPERS
    # ----------------------------------------------------------

    def _refresh_devices(self):
        devs = get_devices()
        vals = [f"{d['serial']}  [{d['state']}]" for d in devs]
        self.dev_combo["values"] = vals
        if vals:
            self.dev_combo.current(0)
            self.serial.set(devs[0]["serial"])
            self._log(f"device: {devs[0]['serial']} [{devs[0]['state']}]")
            self._ghost_say(f"device locked: {devs[0]['serial']} -- lets get to work")
            # show model
            def _fetch():
                info = get_device_info(self.serial.get())
                model = f"{info.get('Brand','')} {info.get('Model','')} Android {info.get('Android','')}"
                self.dev_info_lbl.config(text=model, fg=GOLD)
            threading.Thread(target=_fetch, daemon=True).start()
        else:
            self.serial.set("")
            self.dev_info_lbl.config(text="no devices", fg=BLOOD)
            self._ghost_say("no devices detected -- connect USB or use wireless ADB")

    def _get_serial(self):
        s = self.serial.get().strip()
        # strip the [state] suffix if present
        if "  [" in s:
            s = s.split("  [")[0].strip()
        return s if s else None

    # ----------------------------------------------------------
    # LOG + GHOST
    # ----------------------------------------------------------

    def _log(self, msg):
        self.log.config(state=tk.NORMAL)
        ts = time.strftime("%H:%M:%S")
        self.log.insert(tk.END, f"[{ts}] {msg}\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)

    def _ghost_say(self, msg):
        self.ghost_var.set(msg[:90])

    def _idle_timer(self):
        phrase = self._idle_phrases[self._idle_idx % len(self._idle_phrases)]
        self._idle_idx += 1
        self._ghost_say(phrase)
        self.root.after(14000, self._idle_timer)

    # ----------------------------------------------------------
    # FRP ACTIONS
    # ----------------------------------------------------------

    def _run_frp(self, key):
        m = ALL_FRP_METHODS.get(key) or FRP_METHODS.get(key, {})
        if not m: return
        serial   = self._get_serial()
        prefix   = ["-s", serial] if serial else []
        info     = get_device_info(serial) if serial else {}
        codename = info.get("Codename", "unknown")
        brand    = info.get("Brand", "")
        model    = info.get("Model", "")

        if m.get("warning"):
            if not messagebox.askyesno("warning",
                    m["warning"] + "\n\ncontinue?"):
                return

        # manual guide methods -- show guide instead
        if m.get("manual") and not m.get("cmds"):
            self._frp_show_guide(key)
            return

        if m.get("fastboot"):
            self._log("rebooting to fastboot for FRP wipe...")
            self._ghost_say("rebooting to fastboot -- wipe FRP partition")
            audit_log("FRP_FASTBOOT_START", f"method {key} {model}", serial)
            adb(*prefix, "reboot", "bootloader")
            self.root.after(9000, lambda: [
                fastboot_cmd("erase", "frp"),
                fastboot_cmd("reboot"),
                self._log("FRP partition wiped via fastboot"),
                audit_log("FRP_FASTBOOT_DONE", f"method {key}", serial),
            ])
            return

        self._ghost_say(f"running FRP method {key}...")
        self._log(f"--- FRP method {key}: {m['name']} ---")
        audit_log("FRP_START", f"method {key} | {brand} {model} | {codename}", serial)

        def _run():
            ok = 0
            fail = 0
            for cmd in m.get("cmds", []):
                code, out, err = adb(*prefix, "shell", cmd)
                if code == 0:
                    self._log(f"  OK   {cmd[:55]}")
                    ok += 1
                else:
                    self._log(f"  FAIL {cmd[:55]}  ({err[:40]})")
                    fail += 1

            success = fail == 0 and ok > 0
            self._log(f"--- done: {ok} ok / {fail} failed ---")
            self._log(f"NEXT: {m.get('post','reboot and test')}")
            self._ghost_say(f"method {key} done -- {m.get('post','')[:70]}")

            # record outcome
            record_attempt(key, codename, success)
            audit_log(
                "FRP_DONE",
                f"method {key} | ok={ok} fail={fail} | {'SUCCESS' if success else 'PARTIAL'}",
                serial,
            )
            # refresh audit log tab
            self.root.after(0, self._frp_load_audit)

        threading.Thread(target=_run, daemon=True).start()

    # ----------------------------------------------------------
    # BLOAT ACTIONS
    # ----------------------------------------------------------

    def _run_bloat(self, profile, pkgs):
        if not messagebox.askyesno("confirm",
                f"remove {len(pkgs)} packages from {profile}?\n"
                "safe -- pm uninstall --user 0 (reversible)"):
            return
        serial = self._get_serial()
        prefix = ["-s", serial] if serial else []
        self._ghost_say(f"nuking {profile} bloat...")
        self._log(f"--- bloat: {profile} ({len(pkgs)} packages) ---")

        def _run():
            removed = 0
            for pkg in pkgs:
                code, out, _ = adb(*prefix, "shell",
                                    f"pm uninstall -k --user 0 {pkg}")
                if "Success" in out:
                    self._log(f"  removed  {pkg}")
                    removed += 1
                else:
                    self._log(f"  skipped  {pkg}")
            self._log(f"--- done: {removed}/{len(pkgs)} removed ---")
            self._ghost_say(f"bloat nuked: {removed}/{len(pkgs)} packages gone")

        threading.Thread(target=_run, daemon=True).start()

    def _run_bloat_all(self):
        all_pkgs = [p for pkgs in BLOAT.values() for p in pkgs]
        self._run_bloat("ALL", all_pkgs)

    def _run_custom_bloat(self):
        pkg = self.custom_pkg.get().strip()
        if not pkg:
            return
        serial = self._get_serial()
        prefix = ["-s", serial] if serial else []
        code, out, err = adb(*prefix, "shell",
                              f"pm uninstall -k --user 0 {pkg}")
        if "Success" in out:
            self._log(f"removed: {pkg}")
            self._ghost_say(f"removed {pkg}")
        else:
            self._log(f"failed: {pkg} -- {err}")
            self._ghost_say(f"package not found or already removed")

    # ----------------------------------------------------------
    # WIRELESS ACTIONS
    # ----------------------------------------------------------

    def _w_tcpip(self):
        serial = self._get_serial()
        prefix = ["-s", serial] if serial else []
        code, out, err = adb(*prefix, "tcpip", "5555")
        self._log(f"tcpip: {out or err}")
        self._ghost_say("tcpip:5555 enabled -- now connect by IP")

    def _w_connect_ip(self):
        ip = self.ip_entry.get().strip()
        if ":" not in ip:
            ip += ":5555"
        code, out, err = adb("connect", ip)
        self._log(f"connect {ip}: {out or err}")
        self._ghost_say(out or err)
        if "connected" in (out or ""):
            self._refresh_devices()

    def _w_pair(self):
        ip   = simpledialog.askstring("pair", "device IP:")
        port = simpledialog.askstring("pair", "pairing port (from Wireless Debugging):")
        code = simpledialog.askstring("pair", "6-digit pairing code:")
        if not all([ip, port, code]):
            return
        r = subprocess.run(["adb", "pair", f"{ip}:{port}", code],
                           capture_output=True, text=True)
        self._log(f"pair: {r.stdout or r.stderr}")
        self._ghost_say(r.stdout.strip()[:80])

    def _w_get_ip(self):
        serial = self._get_serial()
        prefix = ["-s", serial] if serial else []
        _, out, _ = adb(*prefix, "shell", "ip addr show wlan0")
        for line in out.splitlines():
            if "inet " in line:
                self._log(f"wlan0: {line.strip()}")
                self._ghost_say(line.strip()[:80])
                return
        self._log("no wlan0 IP found")

    def _w_disconnect(self):
        adb("disconnect")
        self._log("all wireless ADB sessions disconnected")
        self._ghost_say("wireless ADB cleared")
        self._refresh_devices()

    # ----------------------------------------------------------
    # TOOLS ACTIONS
    # ----------------------------------------------------------

    def _t_info(self):
        serial = self._get_serial()
        info = get_device_info(serial)
        self._log("--- device info ---")
        for k, v in info.items():
            self._log(f"  {k}: {v}")
        self._log("-------------------")
        self._ghost_say(f"{info.get('Brand','')} {info.get('Model','')} Android {info.get('Android','')}")

    def _t_reboot(self, mode):
        serial = self._get_serial()
        prefix = ["-s", serial] if serial else []
        modes = {
            "normal":     ["reboot"],
            "recovery":   ["reboot", "recovery"],
            "bootloader": ["reboot", "bootloader"],
            "download":   ["reboot", "download"],
        }
        adb(*prefix, *modes[mode])
        self._log(f"rebooting: {mode}")
        self._ghost_say(f"rebooting to {mode}...")

    def _t_screenshot(self):
        serial = self._get_serial()
        prefix = ["-s", serial] if serial else []
        fname = f"sw_screen_{int(time.time())}.png"
        adb(*prefix, "shell", f"screencap -p /sdcard/{fname}")
        code, out, err = adb(*prefix, "pull", f"/sdcard/{fname}", f"./{fname}")
        adb(*prefix, "shell", f"rm /sdcard/{fname}")
        if code == 0:
            self._log(f"screenshot saved: ./{fname}")
            self._ghost_say(f"screenshot saved: {fname}")
        else:
            self._log(f"screenshot failed: {err}")

    def _t_oem(self):
        serial = self._get_serial()
        prefix = ["-s", serial] if serial else []
        code, out, err = adb(*prefix, "shell",
                              "settings put global oem_unlock_allowed 1")
        self._log("OEM unlock flag set -- reboot to apply")
        self._ghost_say("OEM unlock flag set")

    def _t_adb_enable(self):
        serial = self._get_serial()
        prefix = ["-s", serial] if serial else []
        adb(*prefix, "shell", "settings put global adb_enabled 1")
        self._log("ADB enabled")
        self._ghost_say("ADB enabled on device")

    def _t_install_apk(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="select APK",
            filetypes=[("APK files", "*.apk"), ("All files", "*.*")]
        )
        if not path:
            return
        serial = self._get_serial()
        prefix = ["-s", serial] if serial else []
        self._log(f"installing: {os.path.basename(path)}")

        def _run():
            code, out, err = adb(*prefix, "install", "-r", path)
            self._log(f"install: {out or err}")
            self._ghost_say("APK installed" if "Success" in out else f"install failed: {err[:60]}")

        threading.Thread(target=_run, daemon=True).start()

    def _t_custom_cmd(self):
        cmd = simpledialog.askstring("ADB shell", "enter adb shell command:")
        if not cmd:
            return
        serial = self._get_serial()
        _, out, err = adb_shell(cmd, serial)
        self._log(f"$ {cmd}")
        self._log(out or err or "(no output)")
        self._ghost_say((out or err or "done")[:80])

    # ----------------------------------------------------------
    # AI ACTIONS
    # ----------------------------------------------------------

    def _update_ai_status(self):
        parts = []
        if _load_key(KEY_FILE):   parts.append("Claude: ready")
        if _load_key(GROQ_KEY_FILE): parts.append("Groq: ready")
        parts.append("Ollama: local")
        parts.append("Offline: always")
        self.ai_status_var.set("  " + "  |  ".join(parts))

    def _chat_append(self, text, tag="reply"):
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.insert(tk.END, text, tag)
        self.chat_log.see(tk.END)
        self.chat_log.config(state=tk.DISABLED)

    def _send_ai(self):
        msg = self.ai_input.get().strip()
        if not msg:
            return
        self.ai_input.delete(0, tk.END)

        serial = self._get_serial()
        device_ctx = ""
        if serial:
            info = get_device_info(serial)
            device_ctx = (f"{info.get('Brand','')} {info.get('Model','')} "
                          f"Android {info.get('Android','')} "
                          f"patch:{info.get('Patch','')}")

        self._chat_append(f"\nyou  >  {msg}\n", "user")
        self._ghost_say(random.choice([
            "thinking...", "consulting the void...",
            "ghost brain engaged...", "pulling from kernel space..."
        ]))

        self.ai_history.append({"role": "user", "content": msg})

        def _run():
            reply, source = ghosteey_ask(msg, self.ai_history[:-1], device_ctx)
            self.ai_history.append({"role": "assistant", "content": reply})
            if len(self.ai_history) > 20:
                self.ai_history = self.ai_history[-16:]

            self.root.after(0, lambda: [
                self._chat_append(f"\nghost [{source}]  >\n", "ghost"),
                self._chat_append(reply + "\n", "reply"),
                self._ghost_say(reply[:80]),
            ])

        threading.Thread(target=_run, daemon=True).start()

    def _clear_chat(self):
        self.ai_history = []
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.delete("1.0", tk.END)
        self.chat_log.config(state=tk.DISABLED)
        self._ghost_say("memory wiped. fresh start.")

# ============================================================
#  ENTRY
# ============================================================

def main():
    # check adb on startup
    if not shutil.which("adb"):
        print("WARNING: adb not found in PATH")
        print("download platform-tools: developer.android.com/tools/releases/platform-tools")
        print("add to PATH then rerun")
        print("continuing anyway...")

    root = tk.Tk()

    # icon / taskbar
    try:
        root.iconbitmap(default="")
    except Exception:
        pass

    app = SoulWoRnGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
