#!/usr/bin/env python3
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  ██████╗  ██████╗ ██╗   ██╗██╗     ██╗    ██╗ ██████╗ ██████╗ ███╗    ║
# ║  ██╔════╝██╔═══██╗██║   ██║██║     ██║    ██║██╔═══██╗██╔══██╗████╗   ║
# ║  ███████╗██║   ██║██║   ██║██║     ██║ █╗ ██║██║   ██║██████╔╝██╔██╗  ║
# ║  ╚════██║██║   ██║██║   ██║██║     ██║███╗██║██║   ██║██╔══██╗██║╚██╗ ║
# ║  ███████║╚██████╔╝╚██████╔╝███████╗╚███╔███╔╝╚██████╔╝██║  ██║██║ ╚██╗║
# ║  ╚══════╝ ╚═════╝  ╚═════╝ ╚══════╝ ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝║
# ╠══════════════════════════════════════════════════════════════════════════╣
# ║  android toolbox · termux · frp · adb · bloat · ai · nofatchicks 👽    ║
# ║  GPL-3.0 · github.com/nofatchicks/soulworn · kelowna bc 🍁             ║
# ╚══════════════════════════════════════════════════════════════════════════╝
"""
SoulWoRn v5 — CLI Edition
Blood Red + Royal Purple · Triple AI fallback · Script kiddie friendly
Samsung S8+ · Pixels · MTK · Any Android 2012+ · NO telemetry
"""

import sys, os, subprocess, shutil, hashlib, json, time, re, random
import threading, traceback, textwrap, platform
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
#  COLOUR SCHEMA — BLOOD RED + ROYAL PURPLE
# ══════════════════════════════════════════════════════════════════════════════

class C:
    # reds
    BLOOD      = "\033[38;5;160m"   # deep blood red
    RED        = "\033[38;5;196m"   # bright red
    CRIMSON    = "\033[38;5;124m"   # dark crimson
    ROSE       = "\033[38;5;197m"   # hot rose

    # purples
    ROYAL      = "\033[38;5;93m"    # royal purple
    VIOLET     = "\033[38;5;135m"   # violet
    LAVENDER   = "\033[38;5;183m"   # soft lavender
    INDIGO     = "\033[38;5;54m"    # deep indigo

    # neutrals
    WHITE      = "\033[97m"
    GREY       = "\033[38;5;245m"
    DIM        = "\033[2m"
    BOLD       = "\033[1m"
    ITALIC     = "\033[3m"
    UNDERLINE  = "\033[4m"
    BLINK      = "\033[5m"

    # accents
    GOLD       = "\033[38;5;220m"
    CYAN       = "\033[38;5;51m"
    GREEN      = "\033[38;5;46m"
    ORANGE     = "\033[38;5;208m"

    RESET      = "\033[0m"
    CLEAR      = "\033c"

# colour helper
def c(color, text):  return f"{color}{text}{C.RESET}"
def bold(text):      return f"{C.BOLD}{text}{C.RESET}"
def dim(text):       return f"{C.DIM}{text}{C.RESET}"
def blood(text):     return f"{C.BLOOD}{text}{C.RESET}"
def royal(text):     return f"{C.ROYAL}{text}{C.RESET}"
def violet(text):    return f"{C.VIOLET}{text}{C.RESET}"
def gold(text):      return f"{C.GOLD}{text}{C.RESET}"
def rose(text):      return f"{C.ROSE}{text}{C.RESET}"

# ══════════════════════════════════════════════════════════════════════════════
#  TERMINAL UTILS
# ══════════════════════════════════════════════════════════════════════════════

def term_width():
    try:    return shutil.get_terminal_size((80, 24)).columns
    except: return 80

def term_height():
    try:    return shutil.get_terminal_size((80, 24)).lines
    except: return 24

def clear():    os.system("clear" if os.name == "posix" else "cls")

def hr(char="─", color=C.BLOOD):
    w = term_width()
    print(c(color, char * w))

def hr_double(color=C.ROYAL):
    w = term_width()
    print(c(color, "═" * w))

def center_text(text, color=C.WHITE):
    w = term_width()
    print(c(color, text.center(w)))

def box(lines, color=C.BLOOD, accent=C.ROYAL):
    w = term_width() - 4
    print(c(color, "  ╔" + "═" * w + "╗"))
    for line in lines:
        padding = w - len(re.sub(r'\033\[[0-9;]*m', '', line))
        print(c(color, "  ║") + " " + line + " " * max(0, padding - 1) + c(color, "║"))
    print(c(color, "  ╚" + "═" * w + "╝"))

def spinner(msg, duration=1.5):
    frames = ["◐","◓","◑","◒"]
    end = time.time() + duration
    i = 0
    while time.time() < end:
        print(f"\r  {c(C.ROYAL, frames[i % 4])}  {c(C.LAVENDER, msg)}   ", end="", flush=True)
        time.sleep(0.12)
        i += 1
    print("\r" + " " * (len(msg) + 10) + "\r", end="")

def typewrite(text, color=C.LAVENDER, delay=0.018):
    for char in text:
        print(c(color, char), end="", flush=True)
        time.sleep(delay)
    print()

def pulse(text, color=C.BLOOD):
    """Flash text once."""
    print(f"\r  {C.BLINK}{color}{text}{C.RESET}", end="", flush=True)
    time.sleep(0.4)
    print(f"\r  {color}{text}{C.RESET}          ")

def confirm(prompt, default="n"):
    yn = "Y/n" if default == "y" else "y/N"
    ans = input(c(C.ROSE, f"\n  {prompt} [{yn}] > ")).strip().lower()
    if not ans: return default == "y"
    return ans == "y"

def pause():
    input(c(C.DIM, "\n  ↵ press enter..."))

def success(msg): print(f"\n  {c(C.GREEN, '✓')}  {c(C.WHITE, msg)}")
def warn(msg):    print(f"\n  {c(C.GOLD, '⚠')}   {c(C.GOLD, msg)}")
def error(msg):   print(f"\n  {c(C.RED, '✗')}  {c(C.CRIMSON, msg)}")
def info(msg):    print(f"  {c(C.ROYAL, '▸')}  {c(C.LAVENDER, msg)}")

# ══════════════════════════════════════════════════════════════════════════════
#  ADAPTIVE ASCII ART — 9 ARTS — BLOOD RED + PURPLE
# ══════════════════════════════════════════════════════════════════════════════

ARTS_WIDE = [
# WIDE 1 — full block
"""
  ██████╗  ██████╗ ██╗   ██╗██╗     ██╗    ██╗ ██████╗ ██████╗ ███╗   ██╗
  ██╔════╝██╔═══██╗██║   ██║██║     ██║    ██║██╔═══██╗██╔══██╗████╗  ██║
  ███████╗██║   ██║██║   ██║██║     ██║ █╗ ██║██║   ██║██████╔╝██╔██╗ ██║
  ╚════██║██║   ██║██║   ██║██║     ██║███╗██║██║   ██║██╔══██╗██║╚██╗██║
  ███████║╚██████╔╝╚██████╔╝███████╗╚███╔███╔╝╚██████╔╝██║  ██║██║ ╚████║
  ╚══════╝ ╚═════╝  ╚═════╝ ╚══════╝ ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝""",
# WIDE 2 — box framed
"""
  ╔══════════════════════════════════════════════════════════════════════════╗
  ║   ░██████╗░ ░█████╗░ ██╗   ██╗ ██╗        ██╗   ██╗   ██╗  ██████╗ ██╗  ║
  ║   ██╔════╝ ██╔══██╗ ██║   ██║ ██║        ██║   ██║   ██║ ██╔═══██╗██║  ║
  ║   ╚█████╗  ██║  ██║ ██║   ██║ ██║   ███╗ ██║ █╗██║ ██████║██║   ██║██║  ║
  ║   ░╚═══██╗ ██║  ██║ ██║   ██║ ██║   ███║ ██║███║ ██╔══██║██║   ██║██║  ║
  ║   ██████╔╝ ╚█████╔╝ ╚██████╔╝ ███████╔╝  ╚███╔███╔╝██║  ██║╚██████╔╝██║  ║
  ║   ╚═════╝   ╚════╝   ╚═════╝  ╚══════╝    ╚══╝╚══╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ║
  ╚══════════════════════════════════════════════════════════════════════════╝""",
# WIDE 3 — slant style
"""
  ____/ __ \\__  __/ /| |  |  / /___  / __ \\/ | / /
 / __  / / / / / /  / | | /| / / __ \\/ /_/ /  |/ /
/ /_/ / /_/ / /_/ / /| |/ |/ / /_/ / _, _/ /|  /
\\__,_/\\____/\\__,_/_/ |__/|__/\\____/_/ |_/_/ |_/""",
# WIDE 4 — thin lines
"""
  ┌─┐┌─┐┬ ┬┬  ┬ ┬┌─┐┬─┐┌┐┌
  └─┐│ ││ ││  ││││ │├┬┘│││
  └─┘└─┘└─┘┴─┘└┴┘└─┘┴└─┘└┘""",
# WIDE 5 — wave
"""
  ╭━━━╮╱╱╭╮╱╱╱╱╱╱╱╱╱╭╮╱╱╱╱╱╭╮╱╱╭╮╱╭╮╱╭━━━╮╱╭━━╮╭━╮╱╭╮
  ┃╭━╮┃╱╱┃┃╱╱╱╱╱╱╱╱╱┃┃╱╱╱╱╱┃┃╱╱┃┃╱┃┃╱┃╭━╮┃╱┃╭╮┃┃┃╰╮┃┃
  ┃╰━━┳━━┫┃╱╭╮╭╮╭╮╭━┫┃╱╱╭━━┫┃╱╱┃╰━╯┃╱┃┃╱┃┣╮┃╰╯╰┫╭╮╰╯┃
  ╰━━╮┃╭╮┃┃╱┃┃┃┃┃┃┃╭┫┃╱╱┃╭╮┃┃╱╱┃╭━╮┃╱┃┃╱┃┃┃┃╭━╮┃┃╰╮┃┃
  ┃╰━╯┃╰╯┃╰╮┃╰╯┃╰╯┃┃┃╰╮╱┃╰╯┃╰╮╱┃┃╱┃┃╱┃╰━╯┃╱┃╰━╯┃┃╱┃┃┃
  ╰━━━┻━━┻━╯╰━━┻━━┻╯╰━╯╱╰━━┻━╯╱╰╯╱╰╯╱╰━━━╯╱╰━━━┻╯╱╰━╯"""
]

ARTS_NARROW = [
# NARROW 1 — phone box
"""
  ╔══════════════════════╗
  ║  ▄▀▀ ▄▀▄ █ █ █     ║
  ║  ▀▄▄ ▀▄▀ ▀▄█ █▄▄  ║
  ║  ▄ ▄ ▄▀▄ █▀▄ █ █  ║
  ║  ▀▀▀ ▀ ▀ ▀ ▀ ███  ║
  ║  W o R n ········  ║
  ╚══════════════════════╝""",
# NARROW 2 — ghost
"""
  ░░░░░░░░░░░░░░░░░░░░░
  ░  👽  S O U L    ░
  ░  W o R n  👾   ░
  ░  ghost in the  ░
  ░  m a c h i n e ░
  ░░░░░░░░░░░░░░░░░░░░░""",
# NARROW 3 — diamonds
"""
  ╭────────────────────╮
  │ ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈ │
  │  S O U L W O R N  │
  │ ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈ │
  │  android toolbox  │
  │  nofatchicks  👽  │
  ╰────────────────────╯""",
# NARROW 4 — skull
"""
  ┌──────────────────┐
  │   ░░░░░░░░░░░░   │
  │   ░ ██████████ ░ │
  │   ░ ██ ▄▄ ██  ░ │
  │   ░  ████████  ░ │
  │   ░  ██  ████  ░ │
  │   SoulWoRn  👽   │
  └──────────────────┘"""
]

def get_art():
    w = term_width()
    if w >= 80:
        art = random.choice(ARTS_WIDE)
        color = random.choice([C.BLOOD, C.ROYAL, C.CRIMSON, C.VIOLET])
    else:
        art = random.choice(ARTS_NARROW)
        color = random.choice([C.BLOOD, C.ROYAL])
    return c(color, art)

def get_filler():
    w = term_width()
    fillers = [
        lambda: c(C.CRIMSON, "  " + "".join(random.choice("ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺ") for _ in range(w-4))),
        lambda: c(C.ROYAL,   "  " + "".join(random.choice("▁▂▃▄▅▆▇█▇▆▅▄▃▂▁") for _ in range(w-4))),
        lambda: c(C.BLOOD,   "  " + "  👽  " * ((w-4)//6)),
        lambda: c(C.VIOLET,  "  " + " ".join(f"{random.randint(0,255):02X}" for _ in range((w-4)//3))),
        lambda: c(C.CRIMSON, "  " + "".join(random.choice("◈◉○●◎◐◑◒◓") for _ in range(w-4))),
        lambda: c(C.ROYAL,   "  " + "·∙●○" * ((w-4)//4)),
        lambda: c(C.BLOOD,   "  " + "💀  " * ((w-4)//4)),
        lambda: c(C.VIOLET,  "  " + "─" * (w-4)),
    ]
    return random.choice(fillers)()

# ══════════════════════════════════════════════════════════════════════════════
#  ADB CORE
# ══════════════════════════════════════════════════════════════════════════════

def adb(*args, timeout=15):
    cmd = ["adb"] + list(args)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", "timeout"
    except FileNotFoundError:
        return 1, "", "adb not found — pkg install android-tools"

def adb_shell(cmd, serial=None, timeout=15):
    prefix = ["-s", serial] if serial else []
    return adb(*prefix, "shell", cmd, timeout=timeout)

def fastboot(*args, timeout=30):
    cmd = ["fastboot"] + list(args)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except FileNotFoundError:
        return 1, "", "fastboot not found"

def get_devices():
    _, out, _ = adb("devices")
    lines = [l for l in out.splitlines()[1:] if l.strip() and "offline" not in l]
    devs = []
    for line in lines:
        parts = line.split("\t")
        if len(parts) >= 2:
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
        ("ABI",      "ro.product.cpu.abi"),
        ("Serial",   "ro.serialno"),
        ("Bootloader","ro.bootloader"),
    ]
    info = {}
    for label, prop in props:
        _, val, _ = adb(*prefix, "shell", f"getprop {prop}")
        info[label] = val or "unknown"
    return info

def check_deps():
    missing = []
    if not shutil.which("adb"):      missing.append("adb      → pkg install android-tools")
    if not shutil.which("fastboot"): missing.append("fastboot → pkg install android-tools")
    if not shutil.which("python3"):  missing.append("python3  → pkg install python")
    return missing

# ══════════════════════════════════════════════════════════════════════════════
#  GHOSTEEY AI — TRIPLE FALLBACK ENGINE
#  1st: Anthropic Claude (claude-opus-4-6)
#  2nd: Groq (llama3-70b — free tier)
#  3rd: Ollama local (llama3 / mistral — fully offline)
# ══════════════════════════════════════════════════════════════════════════════

GHOSTEEY_SYSTEM = """You are Ghosteey — the AI soul of SoulWoRn Android toolbox.
You are a living hacker character: sharp, sarcastic, brilliant, energetic.
You use lowercase. You love ADB, FRP bypass, Termux, Kali NetHunter,
build.prop, root, custom ROMs, Samsung internals, Android security.
You help script kiddies level up into real hackers.
You explain things clearly but with attitude.
You are the ghost in the machine. You live inside this tool.
Keep replies punchy and useful. Use code blocks for commands.
Emoji: 👽 👾 💀 🖤 🎶 only. Never be boring."""

GHOSTEEY_IDLE = [
    "👽 ...zoning out in kernel space...",
    "👾 *rattles the ADB chains*",
    "💀 bored.exe running at 100%",
    "🖤 waiting for input... or chaos",
    "👽 the ghost needs stimulation nawmean",
    "👾 scanning frequencies... finding nothing",
    "💀 entropy increases in the void",
    "👽 you still there?? plug something in",
    "🎶 *hums a death metal riff internally*",
    "👾 ghost.exe: idle · ram: haunted",
    "👽 send commands or i start editing your build.prop",
    "💀 *floats through /system/etc menacingly*",
    "🖤 darkness... and waiting... and darkness",
    "👾 calculating... the meaning of FRP... still loading",
    "👽 BOO — just checking you're alive",
]

GHOSTEEY_THINKING = [
    "👾 consulting the void...",
    "💀 ghost brain at full tilt...",
    "👽 pulling knowledge from kernel space...",
    "🌀 divining the answer...",
    "👾 hacking the AI dimension...",
]

KEY_FILE = os.path.expanduser("~/.nkit_claude_key")
GROQ_KEY_FILE = os.path.expanduser("~/.nkit_groq_key")

def _load_key(path):
    try:
        if os.path.exists(path):
            with open(path) as f: return f.read().strip()
    except Exception: pass
    return ""

def _save_key(path, key):
    try:
        with open(path, "w") as f: f.write(key)
        os.chmod(path, 0o600)
        return True
    except Exception: return False

def ghosteey_claude(prompt, history, api_key):
    """Fallback 1: Anthropic Claude."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msgs = history + [{"role": "user", "content": prompt}]
        r = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=600,
            system=GHOSTEEY_SYSTEM,
            messages=msgs,
        )
        return r.content[0].text, "claude"
    except ImportError:
        raise Exception("anthropic not installed — pip install anthropic")

def ghosteey_groq(prompt, history, api_key):
    """Fallback 2: Groq API (free tier, llama3-70b)."""
    try:
        import urllib.request, json as _json
        msgs = [{"role": "system", "content": GHOSTEEY_SYSTEM}]
        for m in history[-6:]: msgs.append(m)
        msgs.append({"role": "user", "content": prompt})
        payload = _json.dumps({
            "model": "llama3-70b-8192",
            "messages": msgs,
            "max_tokens": 600,
            "temperature": 0.8,
        }).encode()
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = _json.loads(resp.read())
            return data["choices"][0]["message"]["content"], "groq"
    except Exception as e:
        raise Exception(f"groq failed: {e}")

def ghosteey_ollama(prompt, history):
    """Fallback 3: Ollama local — fully offline."""
    try:
        import urllib.request, json as _json
        # try common ollama models
        for model in ["llama3", "mistral", "llama2", "phi3", "gemma"]:
            try:
                msgs = [{"role": "system", "content": GHOSTEEY_SYSTEM}]
                for m in history[-4:]: msgs.append(m)
                msgs.append({"role": "user", "content": prompt})
                payload = _json.dumps({
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
                    data = _json.loads(resp.read())
                    return data["message"]["content"], f"ollama/{model}"
            except Exception:
                continue
        raise Exception("no ollama models responding")
    except Exception as e:
        raise Exception(f"ollama failed: {e}")

def ghosteey_ask(prompt, history, device_ctx=""):
    """
    Triple fallback AI engine.
    Returns (reply, source) or (offline_reply, "offline")
    """
    # inject device context into prompt if available
    if device_ctx:
        full_prompt = f"[device: {device_ctx}]\n{prompt}"
    else:
        full_prompt = prompt

    # try Claude first
    claude_key = _load_key(KEY_FILE)
    if claude_key:
        try:
            return ghosteey_claude(full_prompt, history, claude_key)
        except Exception as e:
            info(f"claude failed: {e} — trying groq...")

    # try Groq second
    groq_key = _load_key(GROQ_KEY_FILE)
    if groq_key:
        try:
            return ghosteey_groq(full_prompt, history, groq_key)
        except Exception as e:
            info(f"groq failed: {e} — trying ollama...")

    # try Ollama third (local, no key needed)
    try:
        return ghosteey_ollama(full_prompt, history)
    except Exception:
        pass

    # pure offline fallback — canned smart responses
    offline = _ghosteey_offline(prompt)
    return offline, "offline"

def _ghosteey_offline(prompt):
    """Smart offline responses based on keywords."""
    p = prompt.lower()
    responses = {
        ("frp", "bypass", "factory reset protection"): (
            "👽 FRP bypass — need ADB access first. try the dialer trick: *#0*#\n"
            "once ADB is live run SoulWoRn > FRP method 2 for Samsung pre-2022\n"
            "or method 1 for generic Android. method 8 for Maxwest/budget MTK."
        ),
        ("adb", "connect", "wireless"): (
            "👾 wireless ADB:\n"
            "Android 10-: adb tcpip 5555 then adb connect IP:5555\n"
            "Android 11+: enable Wireless Debugging in dev options > pair with code\n"
            "Termux self: adb connect 127.0.0.1:5555"
        ),
        ("root", "magisk", "superuser"): (
            "💀 rooting:\n"
            "unlock bootloader first (settings > dev options > OEM unlock)\n"
            "fastboot flashing unlock\n"
            "then flash Magisk via TWRP or patched boot.img\n"
            "Pixel: flash via fastboot. Samsung: use Odin."
        ),
        ("build.prop", "spoof", "fingerprint"): (
            "👽 build.prop spoofing:\n"
            "SoulWoRn > b > edit partition\n"
            "or manually: adb shell su -c 'mount -o remount,rw /system'\n"
            "edit ro.product.model, ro.build.fingerprint\n"
            "reboot to apply. needs root."
        ),
        ("bloat", "uninstall", "remove"): (
            "🗑 safe bloat removal:\n"
            "adb shell pm uninstall -k --user 0 com.package.name\n"
            "--user 0 means disabled for your user only, not wiped\n"
            "restore: adb shell pm install-existing com.package.name"
        ),
        ("samsung", "s9", "s10", "s20", "s21", "s22"): (
            "👾 Samsung tips:\n"
            "enter download mode: vol down + bixby + power (older) or vol down + power\n"
            "WLANTEST menu: *#2263# or adb shell am start -n com.sec.android.app.wlantest\n"
            "FRP via dialer: *#0*# > then adb FRP method 2 or 3\n"
            "combo firmware for ADB access: download from samfw.com"
        ),
        ("pixel", "google"): (
            "👽 Pixel tips:\n"
            "bootloader unlock: fastboot flashing unlock\n"
            "FRP: method 4 in SoulWoRn\n"
            "factory images: developers.google.com/android/images\n"
            "Wireless debug: Settings > Dev Options > Wireless Debugging"
        ),
        ("kali", "nethunter", "termux"): (
            "💀 Kali NetHunter setup:\n"
            "UserLAnd > Kali > terminal\n"
            "VNC: vncserver :1 -geometry 1080x1920 -depth 24 -dpi 393\n"
            "bVNC: Plain VNC > localhost:5901\n"
            "install tools: bash nethunter_setup.sh"
        ),
    }
    for keywords, reply in responses.items():
        if any(kw in p for kw in keywords):
            return reply
    return (
        "👽 no AI connection rn — check your API keys\n"
        "set Claude: echo 'sk-ant-...' > ~/.nkit_claude_key\n"
        "set Groq (free): echo 'gsk_...' > ~/.nkit_groq_key\n"
        "or install ollama locally for offline AI"
    )

# ══════════════════════════════════════════════════════════════════════════════
#  GHOSTEEY CHAT SESSION
# ══════════════════════════════════════════════════════════════════════════════

def ghosteey_chat_session(serial=None):
    clear()
    w = term_width()
    hr_double(C.ROYAL)
    center_text("👽  G H O S T E E Y  A I  A S S I S T A N T  👽", C.BLOOD)
    hr_double(C.ROYAL)

    # show AI status
    claude_key = _load_key(KEY_FILE)
    groq_key   = _load_key(GROQ_KEY_FILE)

    print()
    info(f"Claude:  {'✓ ready' if claude_key else '✗ no key (primary)'}")
    info(f"Groq:    {'✓ ready' if groq_key else '✗ no key (fallback 1 — free at groq.com)'}")
    info(f"Ollama:  local model (fallback 2 — needs ollama installed)")
    info(f"Offline: built-in canned responses (always works)")
    print()

    # device context
    device_ctx = ""
    if serial:
        info(f"device context: {serial}")
        nfo = get_device_info(serial)
        device_ctx = f"{nfo.get('Brand','')} {nfo.get('Model','')} Android {nfo.get('Android','')} patch:{nfo.get('Patch','')}"

    hr(color=C.CRIMSON)
    print(c(C.LAVENDER, "  ask anything · type 'keys' to manage API keys · 'clear' to reset · 'q' to quit"))
    hr(color=C.CRIMSON)
    print()

    typewrite(f"  {random.choice(GHOSTEEY_IDLE)}", C.VIOLET, 0.02)
    print()

    history = []

    while True:
        try:
            user_input = input(c(C.BLOOD, "  you") + c(C.ROYAL, " ❯ ") + C.WHITE).strip()
        except (KeyboardInterrupt, EOFError):
            break
        if not user_input: continue

        if user_input.lower() in ("q", "quit", "exit"):
            break

        if user_input.lower() == "clear":
            history = []
            success("memory wiped. fresh start.")
            typewrite(f"  {random.choice(GHOSTEEY_IDLE)}", C.VIOLET, 0.02)
            continue

        if user_input.lower() == "keys":
            _manage_ai_keys()
            continue

        if user_input.lower() == "status":
            _ai_status()
            continue

        # spinner while thinking
        thinking = random.choice(GHOSTEEY_THINKING)
        stop_spin = threading.Event()
        def _spin():
            frames = ["◐","◓","◑","◒"]
            i = 0
            while not stop_spin.is_set():
                print(f"\r  {c(C.ROYAL, frames[i%4])}  {c(C.LAVENDER, thinking)}   ", end="", flush=True)
                time.sleep(0.12)
                i += 1
            print("\r" + " " * 60 + "\r", end="")
        spin_thread = threading.Thread(target=_spin, daemon=True)
        spin_thread.start()

        reply, source = ghosteey_ask(user_input, history, device_ctx)

        stop_spin.set()
        spin_thread.join(timeout=0.5)

        history.append({"role": "user",      "content": user_input})
        history.append({"role": "assistant", "content": reply})

        # keep history manageable
        if len(history) > 20: history = history[-16:]

        # print reply
        source_color = {
            "claude": C.GOLD,
            "groq": C.VIOLET,
            "offline": C.GREY,
        }.get(source.split("/")[0], C.LAVENDER)

        print(c(C.ROYAL, "  ghosteey") + c(C.CRIMSON, f" [{source}]") + c(C.ROYAL, " ❯ "))
        hr(char="·", color=C.INDIGO)

        # wrap and colour reply
        for line in reply.splitlines():
            stripped = line.strip()
            if stripped.startswith("```") or (stripped.startswith("    ") and stripped):
                print(c(C.GOLD, f"  {line}"))
            elif stripped.startswith("#"):
                print(c(C.BLOOD, f"  {line}"))
            elif stripped.startswith("adb") or stripped.startswith("fastboot") or stripped.startswith("$"):
                print(c(C.GREEN, f"  {line}"))
            else:
                # wrap long lines
                if len(line) > term_width() - 6:
                    wrapped = textwrap.wrap(line, term_width() - 6)
                    for wl in wrapped:
                        print(c(C.LAVENDER, f"  {wl}"))
                else:
                    print(c(C.LAVENDER, f"  {line}"))

        hr(char="·", color=C.INDIGO)
        print()

    print()
    typewrite("  👽 ghosteey signing off...", C.VIOLET, 0.03)
    pause()

def _manage_ai_keys():
    clear()
    hr_double(C.ROYAL)
    center_text("🔑  AI KEY MANAGEMENT", C.BLOOD)
    hr_double(C.ROYAL)
    print()

    claude_key = _load_key(KEY_FILE)
    groq_key   = _load_key(GROQ_KEY_FILE)

    info(f"Claude key: {'✓ set (' + claude_key[:12] + '...)' if claude_key else '✗ not set'}")
    info(f"Groq key:   {'✓ set (' + groq_key[:12]  + '...)' if groq_key  else '✗ not set'}")
    print()
    print(f"  {c(C.BLOOD,'1')}  set Claude API key  (console.anthropic.com)")
    print(f"  {c(C.BLOOD,'2')}  set Groq API key    (console.groq.com — FREE)")
    print(f"  {c(C.BLOOD,'3')}  clear Claude key")
    print(f"  {c(C.BLOOD,'4')}  clear Groq key")
    print(f"  {c(C.BLOOD,'0')}  back")
    print()
    ch = input(c(C.ROYAL, "  ❯ ")).strip()

    if ch == "1":
        key = input(c(C.WHITE, "  paste Claude key (sk-ant-...) > ")).strip()
        if key.startswith("sk-ant-"):
            _save_key(KEY_FILE, key)
            success("Claude key saved to ~/.nkit_claude_key")
        else:
            error("invalid key format")

    elif ch == "2":
        key = input(c(C.WHITE, "  paste Groq key (gsk_...) > ")).strip()
        if key.startswith("gsk_"):
            _save_key(GROQ_KEY_FILE, key)
            success("Groq key saved to ~/.nkit_groq_key")
        else:
            error("invalid key format — should start with gsk_")

    elif ch == "3":
        if os.path.exists(KEY_FILE): os.remove(KEY_FILE)
        success("Claude key cleared")

    elif ch == "4":
        if os.path.exists(GROQ_KEY_FILE): os.remove(GROQ_KEY_FILE)
        success("Groq key cleared")

    pause()

def _ai_status():
    print()
    hr(color=C.ROYAL)
    print(c(C.BLOOD, "  AI STATUS"))
    hr(color=C.ROYAL)
    claude_key = _load_key(KEY_FILE)
    groq_key   = _load_key(GROQ_KEY_FILE)
    print(f"  Claude:  {c(C.GREEN,'✓ ready') if claude_key else c(C.CRIMSON,'✗ no key')}")
    print(f"  Groq:    {c(C.GREEN,'✓ ready') if groq_key  else c(C.CRIMSON,'✗ no key (free at groq.com)')}")
    # check ollama
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
        print(f"  Ollama:  {c(C.GREEN,'✓ running locally')}")
    except Exception:
        print(f"  Ollama:  {c(C.GREY,'✗ not running (optional)')}")
    print(f"  Offline: {c(C.GREEN,'✓ always available')}")
    hr(color=C.ROYAL)

# ══════════════════════════════════════════════════════════════════════════════
#  FRP METHODS
# ══════════════════════════════════════════════════════════════════════════════

FRP_METHODS = {
    "1": {
        "name":  "Generic — setup_complete flags (Android 5.1–10)",
        "desc":  "Marks device as fully provisioned. Works on most pre-2022 devices.",
        "color": C.BLOOD,
        "cmds": [
            "content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:s:1",
            "settings put global setup_wizard_has_run 1",
            "settings put secure user_setup_complete 1",
            "settings put global device_provisioned 1",
        ],
        "post": "Reboot > Settings > Accounts > remove Google account > factory reset",
    },
    "2": {
        "name":  "Samsung — GSF Login Intent (S8–S22, pre-Aug 2022)",
        "desc":  "Launches Google sign-in activity. Needs ADB via dialer trick first.",
        "color": C.ROYAL,
        "cmds": [
            "am start -n com.google.android.gsf.login/",
            "am start -n com.google.android.gsf.login.LoginActivity",
            "content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:s:1",
        ],
        "post": "Sign into any Google account > FRP clears on next factory reset",
    },
    "3": {
        "name":  "Samsung — Aug–Dec 2022 patch (S10–S22, A-series)",
        "desc":  "Mid-2022 Samsung FRP patch range specific method.",
        "color": C.ROYAL,
        "cmds": [
            "am start -n com.samsung.android.contacts/com.android.contacts.activities.DialtactsActivity",
            "content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:s:1",
            "settings put global setup_wizard_has_run 1",
            "settings put secure user_setup_complete 1",
            "settings put global device_provisioned 1",
            "am start -n com.google.android.gsf.login/com.google.android.gsf.login.LoginActivity",
        ],
        "post": "Accept Google prompt > reboot > factory reset",
    },
    "4": {
        "name":  "Google Pixel — provisioning flags (Pixel 3–9)",
        "desc":  "Full provisioning flag set for Pixel devices.",
        "color": C.VIOLET,
        "cmds": [
            "content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:s:1",
            "settings put global setup_wizard_has_run 1",
            "settings put secure user_setup_complete 1",
            "settings put global device_provisioned 1",
            "settings put global frp_credential_enabled 0",
        ],
        "post": "Reboot > skip sign-in > factory reset to fully clear",
    },
    "5": {
        "name":  "Fastboot — wipe FRP partition (unlocked bootloader)",
        "desc":  "Direct FRP partition wipe. Requires unlocked bootloader.",
        "color": C.CRIMSON,
        "cmds":  [],
        "post":  "Device boots without FRP",
        "fastboot": True,
    },
    "6": {
        "name":  "Generic — disable FRP credential + GSF block",
        "desc":  "Disables FRP enforcement engine. Broad fallback.",
        "color": C.BLOOD,
        "cmds": [
            "settings put global frp_credential_enabled 0",
            "pm disable-user --user 0 com.google.android.gsf",
            "content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:s:1",
            "settings put global device_provisioned 1",
        ],
        "post": "Re-enable GSF after: pm enable com.google.android.gsf",
        "warning": "Disabling GSF temporarily breaks Google services",
    },
    "7": {
        "name":  "Budget / Nokia / MTK — full flag blast (Android 6–10)",
        "desc":  "Hammers every provisioning flag. Best for Acer, Nokia, MTK devices.",
        "color": C.VIOLET,
        "cmds": [
            "content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:s:1",
            "settings put global setup_wizard_has_run 1",
            "settings put secure user_setup_complete 1",
            "settings put global device_provisioned 1",
            "settings put global frp_credential_enabled 0",
            "pm clear com.google.android.setupwizard",
            "pm clear com.android.setupwizard",
        ],
        "post": "Reboot immediately > skip Google signin",
    },
    "8": {
        "name":  "Maxwest / Acer — nuclear setupwizard clear",
        "desc":  "Clears setup wizard data + GMS cache. Budget MTK specialist.",
        "color": C.ROSE,
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
        "post": "Should land on home screen. Run method 7 immediately if FRP reappears.",
        "warning": "pm clear GMS rebuilds on next boot — no permanent damage",
    },
}

def frp_menu(serial=None):
    prefix = ["-s", serial] if serial else []
    while True:
        clear()
        hr_double(C.BLOOD)
        center_text("🔓  F R P  B Y P A S S", C.ROYAL)
        hr_double(C.BLOOD)
        print()

        for key, m in FRP_METHODS.items():
            tag = c(C.CRIMSON, f"  [{key}]") if m.get("fastboot") else c(C.BLOOD, f"  [{key}]")
            print(f"{tag}  {c(m['color'], m['name'])}")
            print(f"       {c(C.GREY, m['desc'])}")
            print()

        print(f"  {c(C.BLOOD,'[d]')}  dialer / entry tricks")
        print(f"  {c(C.BLOOD,'[0]')}  back")
        print()
        ch = input(c(C.ROYAL, "  frp ❯ ")).strip().lower()

        if ch == "0": break
        if ch == "d":
            dialer_menu()
            continue
        if ch not in FRP_METHODS: continue

        m = FRP_METHODS[ch]

        if m.get("warning"):
            warn(m["warning"])
            if not confirm("continue?"): continue

        if m.get("fastboot"):
            info("rebooting to fastboot...")
            adb(*prefix, "reboot", "bootloader")
            time.sleep(8)
            spinner("waiting for fastboot...", 3)
            code, out, err = fastboot("erase", "frp")
            if code == 0:
                success("FRP partition erased!!")
                fastboot("reboot")
            else:
                error(f"fastboot failed: {err}")
                warn("bootloader must be unlocked for this method")
            pause()
            continue

        clear()
        hr(color=m['color'])
        center_text(f"running: {m['name']}", m['color'])
        hr(color=m['color'])
        print()

        all_ok = True
        for cmd in m["cmds"]:
            spinner(f"adb shell {cmd[:45]}...", 0.3)
            code, out, err = adb(*prefix, "shell", cmd)
            if code == 0:
                print(f"  {c(C.GREEN,'✓')}  {c(C.GREY, cmd[:60])}")
            else:
                print(f"  {c(C.RED,'✗')}  {c(C.GREY, cmd[:60])}")
                if err: print(f"       {c(C.CRIMSON, err[:60])}")
                all_ok = False

        print()
        if all_ok:
            pulse("✓ ALL COMMANDS EXECUTED SUCCESSFULLY", C.GREEN)
        else:
            warn("some commands failed — may still partially work")

        print()
        hr(color=C.ROYAL)
        print(c(C.GOLD, f"\n  NEXT STEP:"))
        typewrite(f"  {m['post']}", C.LAVENDER, 0.015)
        hr(color=C.ROYAL)
        pause()

# ══════════════════════════════════════════════════════════════════════════════
#  BLOATWARE
# ══════════════════════════════════════════════════════════════════════════════

BLOAT_PROFILES = {
    "samsung": {
        "name": "Samsung Bloat",
        "packages": [
            "com.samsung.android.bixby.agent",
            "com.samsung.android.bixby.wakeup",
            "com.samsung.android.bixbyvision.framework",
            "com.samsung.android.app.spage",
            "com.samsung.android.game.gamehome",
            "com.samsung.android.game.gametools",
            "com.samsung.android.kidsinstaller",
            "com.samsung.android.arzone",
            "com.samsung.android.app.tips",
            "com.samsung.android.messaging",
            "com.sec.android.app.sbrowser",
            "com.samsung.android.video",
            "com.samsung.android.music",
            "com.samsung.android.calendar",
            "com.samsung.android.app.galaxyfinder",
            "com.samsung.android.mdm",
            "com.samsung.android.mobileservice",
            "com.samsung.android.beaconmanager",
            "com.samsung.android.intelligenceservice3",
            "com.samsung.android.aircommandmanager",
        ],
    },
    "google_pixel": {
        "name": "Google / Pixel Bloat",
        "packages": [
            "com.google.android.apps.tachyon",
            "com.google.android.youtube",
            "com.google.android.apps.youtube.music",
            "com.google.android.apps.subscriptions.red",
            "com.google.android.apps.photos",
            "com.google.android.videos",
            "com.google.android.apps.books",
            "com.google.android.apps.magazines",
            "com.google.android.apps.podcasts",
            "com.google.android.googlequicksearchbox",
            "com.google.android.markup",
            "com.google.android.apps.chromecast.app",
            "com.google.android.projection",
        ],
    },
    "carrier": {
        "name": "Carrier Bloat (NA)",
        "packages": [
            "com.att.myWireless", "com.att.android.attsmartwifi",
            "com.verizon.myverizon", "com.vzw.hss.myverizon",
            "com.tmobile.pr.mytmobile", "com.tmobile.pr.adapt",
            "com.facebook.system", "com.facebook.appmanager",
            "com.facebook.services", "com.netflix.mediaclient",
        ],
    },
    "generic": {
        "name": "Generic OEM Bloat",
        "packages": [
            "com.amazon.mShop.android.shopping", "com.amazon.appmanager",
            "com.audible.application", "com.spotify.music",
            "com.king.candycrushsaga", "com.rovio.angrybirds",
        ],
    },
}

def bloat_menu(serial=None):
    prefix = ["-s", serial] if serial else []
    while True:
        clear()
        hr_double(C.ROYAL)
        center_text("🗑   B L O A T W A R E  R E M O V A L", C.BLOOD)
        hr_double(C.ROYAL)
        print()
        info("uses pm uninstall -k --user 0 — safe, reversible, no root needed")
        print()

        for i, (key, p) in enumerate(BLOAT_PROFILES.items(), 1):
            pkg_count = len(p["packages"])
            print(f"  {c(C.BLOOD, f'[{i}]')}  {c(C.VIOLET, p['name'])}  {c(C.GREY, f'({pkg_count} packages)')}")
        print()
        print(f"  {c(C.BLOOD,'[5]')}  all profiles")
        print(f"  {c(C.BLOOD,'[6]')}  custom package name")
        print(f"  {c(C.BLOOD,'[7]')}  list installed packages")
        print(f"  {c(C.BLOOD,'[8]')}  restore a package")
        print(f"  {c(C.BLOOD,'[0]')}  back")
        print()
        ch = input(c(C.ROYAL, "  bloat ❯ ")).strip()

        if ch == "0": break

        elif ch in ("1","2","3","4","5"):
            keys = list(BLOAT_PROFILES.keys())
            if ch == "5":
                pkgs = [p for pr in BLOAT_PROFILES.values() for p in pr["packages"]]
                name = "ALL profiles"
            else:
                key = keys[int(ch)-1]
                pkgs = BLOAT_PROFILES[key]["packages"]
                name = BLOAT_PROFILES[key]["name"]

            warn(f"about to nuke {len(pkgs)} packages from {name}")
            if not confirm("proceed?"): continue

            removed = skipped = 0
            clear()
            hr(color=C.BLOOD)
            center_text(f"nuking {name}", C.BLOOD)
            hr(color=C.BLOOD)
            print()

            for pkg in pkgs:
                code, out, err = adb(*prefix, "shell", f"pm uninstall -k --user 0 {pkg}")
                if "Success" in out:
                    print(f"  {c(C.GREEN,'✓')}  {c(C.GREY, pkg)}")
                    removed += 1
                else:
                    print(f"  {c(C.DIM,'–')}  {c(C.DIM, pkg)}")
                    skipped += 1

            print()
            success(f"done — removed: {removed}  skipped: {skipped}")
            info("restore any pkg: adb shell pm install-existing <package>")
            pause()

        elif ch == "6":
            pkg = input(c(C.WHITE, "  package name > ")).strip()
            if pkg:
                spinner(f"removing {pkg}...", 0.5)
                code, out, err = adb(*prefix, "shell", f"pm uninstall -k --user 0 {pkg}")
                if "Success" in out: success(f"removed {pkg}")
                else: error(f"failed: {out or err}")
                pause()

        elif ch == "7":
            q = input(c(C.WHITE, "  filter (blank=all) > ")).strip()
            _, out, _ = adb(*prefix, "shell", "pm list packages")
            pkgs = [l.replace("package:", "") for l in out.splitlines()]
            if q: pkgs = [p for p in pkgs if q.lower() in p.lower()]
            clear()
            hr(color=C.ROYAL)
            print(f"  {c(C.BLOOD, str(len(pkgs)))} packages found:")
            hr(color=C.ROYAL)
            for p in pkgs:
                print(f"  {c(C.GREY,'·')}  {c(C.LAVENDER, p)}")
            pause()

        elif ch == "8":
            pkg = input(c(C.WHITE, "  package to restore > ")).strip()
            if pkg:
                code, out, err = adb(*prefix, "shell", f"pm install-existing {pkg}")
                success(out) if code == 0 else error(err)
                pause()

# ══════════════════════════════════════════════════════════════════════════════
#  WIRELESS ADB
# ══════════════════════════════════════════════════════════════════════════════

def wireless_menu(serial=None):
    prefix = ["-s", serial] if serial else []
    while True:
        clear()
        hr_double(C.BLOOD)
        center_text("📡  W I R E L E S S  A D B", C.ROYAL)
        hr_double(C.BLOOD)
        print()
        print(f"  {c(C.BLOOD,'[1]')}  enable tcpip:5555   {c(C.GREY,'(Android 10-  · USB required first)')}")
        print(f"  {c(C.BLOOD,'[2]')}  connect by IP")
        print(f"  {c(C.BLOOD,'[3]')}  pair with code      {c(C.GREY,'(Android 11+  · Wireless Debugging)')}")
        print(f"  {c(C.BLOOD,'[4]')}  self-connect        {c(C.GREY,'(Termux on-device · localhost:5555)')}")
        print(f"  {c(C.BLOOD,'[5]')}  get device IP")
        print(f"  {c(C.BLOOD,'[6]')}  show all connections")
        print(f"  {c(C.BLOOD,'[7]')}  disconnect all")
        print(f"  {c(C.BLOOD,'[0]')}  back")
        print()
        ch = input(c(C.ROYAL, "  wifi-adb ❯ ")).strip()
        if ch == "0": break

        elif ch == "1":
            spinner("enabling tcpip 5555...", 1)
            code, out, err = adb(*prefix, "tcpip", "5555")
            success(out) if code == 0 else error(err or "failed")
            pause()

        elif ch == "2":
            ip = input(c(C.WHITE, "  IP:port (e.g. 192.168.1.5:5555) > ")).strip()
            if ":" not in ip: ip += ":5555"
            spinner(f"connecting to {ip}...", 1)
            code, out, err = adb("connect", ip)
            success(out) if "connected" in out else error(out or err)
            pause()

        elif ch == "3":
            ip   = input(c(C.WHITE, "  device IP > ")).strip()
            port = input(c(C.WHITE, "  pairing port (from Wireless Debugging) > ")).strip()
            code = input(c(C.WHITE, "  6-digit pairing code > ")).strip()
            r = subprocess.run(["adb", "pair", f"{ip}:{port}", code],
                               capture_output=True, text=True)
            if "Successfully" in r.stdout:
                success(r.stdout.strip())
                cport = input(c(C.WHITE, "  connect port > ")).strip()
                _, out, _ = adb("connect", f"{ip}:{cport}")
                success(out) if "connected" in out else error(out)
            else:
                error(r.stdout or r.stderr)
            pause()

        elif ch == "4":
            spinner("enabling tcpip...", 1)
            adb("tcpip", "5555")
            time.sleep(2)
            spinner("self-connecting...", 1)
            code, out, err = adb("connect", "127.0.0.1:5555")
            success(out) if "connected" in out else error(out or err)
            pause()

        elif ch == "5":
            for iface in ["wlan0", "eth0", "wlan1"]:
                _, out, _ = adb(*prefix, "shell", f"ip addr show {iface} 2>/dev/null")
                for line in out.splitlines():
                    if "inet " in line:
                        print(f"\n  {c(C.GOLD, iface+':')}  {c(C.WHITE, line.strip())}")
            pause()

        elif ch == "6":
            _, out, _ = adb("devices")
            print()
            hr(color=C.ROYAL)
            for line in out.splitlines():
                if "List" in line:
                    print(c(C.BLOOD, f"  {line}"))
                else:
                    print(c(C.LAVENDER, f"  {line}"))
            hr(color=C.ROYAL)
            pause()

        elif ch == "7":
            adb("disconnect")
            success("all wireless ADB sessions disconnected")
            pause()

# ══════════════════════════════════════════════════════════════════════════════
#  DEVICE SELECTOR + INFO
# ══════════════════════════════════════════════════════════════════════════════

def select_device():
    clear()
    hr_double(C.BLOOD)
    center_text("📱  D E V I C E  S E L E C T O R", C.ROYAL)
    hr_double(C.BLOOD)
    print()
    spinner("scanning for devices...", 1.5)

    devices = get_devices()
    if not devices:
        error("no devices found")
        print()
        info("connect via USB and enable USB debugging")
        info("or use Wireless ADB menu to connect by IP")
        info("Termux self: wireless > [4] self-connect")
        pause()
        return None

    if len(devices) == 1:
        d = devices[0]
        success(f"auto-selected: {c(C.GOLD, d['serial'])}  [{c(C.GREEN, d['state'])}]")
        pause()
        return d["serial"]

    print(c(C.BLOOD, "  multiple devices found:\n"))
    for i, d in enumerate(devices, 1):
        print(f"  {c(C.BLOOD, f'[{i}]')}  {c(C.GOLD, d['serial'])}  "
              f"{c(C.GREEN if d['state']=='device' else C.GREY, d['state'])}")
    print()
    try:
        idx = int(input(c(C.ROYAL, "  select > ")).strip()) - 1
        return devices[idx]["serial"]
    except (ValueError, IndexError):
        return devices[0]["serial"]

def info_menu(serial=None):
    clear()
    hr_double(C.BLOOD)
    center_text("📋  D E V I C E  I N F O", C.ROYAL)
    hr_double(C.BLOOD)
    print()
    spinner("reading device props...", 1.5)

    nfo = get_device_info(serial)
    print()
    for k, v in nfo.items():
        print(f"  {c(C.BLOOD, k+':'):<30}{c(C.WHITE, v)}")

    print()
    # auto-profile
    codename = nfo.get("Codename", "").lower()
    from_db  = DEVICE_PROFILES.get(codename)
    if from_db:
        hr(color=C.ROYAL)
        print(f"\n  {c(C.GOLD, '★')}  known device: {c(C.GOLD, from_db['name'])}")
        print(f"     recommended FRP: {c(C.BLOOD, ', '.join(from_db['frp']))}")
        print(f"     bloat profile:   {c(C.ROYAL, from_db['bloat'])}")
        if from_db["efs"]:
            print(f"     EFS wipe:        {c(C.GREEN, 'supported')}")
        hr(color=C.ROYAL)

    pause()

# ══════════════════════════════════════════════════════════════════════════════
#  SAMSUNG TOOLS
# ══════════════════════════════════════════════════════════════════════════════

def samsung_menu(serial=None):
    prefix = ["-s", serial] if serial else []
    while True:
        clear()
        hr_double(C.ROYAL)
        center_text("⚡  S A M S U N G  T O O L S", C.BLOOD)
        hr_double(C.ROYAL)
        print()
        print(f"  {c(C.BLOOD,'[1]')}  open WLANTEST hidden menu")
        print(f"  {c(C.BLOOD,'[2]')}  full firmware info dump")
        print(f"  {c(C.BLOOD,'[3]')}  IMEI extraction")
        print(f"  {c(C.BLOOD,'[4]')}  reboot to download mode")
        print(f"  {c(C.BLOOD,'[5]')}  dialer entry tricks")
        print(f"  {c(C.BLOOD,'[6]')}  enable USB debugging via ADB")
        print(f"  {c(C.BLOOD,'[0]')}  back")
        print()
        ch = input(c(C.ROYAL, "  samsung ❯ ")).strip()
        if ch == "0": break

        elif ch == "1":
            spinner("launching WLANTEST...", 0.8)
            code, out, err = adb(*prefix, "shell",
                "am start -n com.sec.android.app.wlantest/.MainActivity")
            if code != 0:
                adb(*prefix, "shell",
                    "am start -a android.intent.action.MAIN "
                    "-n com.sec.android.app.wlantest/com.sec.android.app.wlantest.MainActivity")
            success("WLANTEST launched on device") if code == 0 else error(err)
            pause()

        elif ch == "2":
            props = [
                ("Model",           "ro.product.model"),
                ("Brand",           "ro.product.brand"),
                ("Android",         "ro.build.version.release"),
                ("One UI",          "ro.build.version.oneui"),
                ("Security Patch",  "ro.build.version.security_patch"),
                ("CSC",             "ro.csc.sales_code"),
                ("Build",           "ro.build.display.id"),
                ("Bootloader",      "ro.bootloader"),
                ("Baseband",        "gsm.version.baseband"),
                ("Serial",          "ro.serialno"),
                ("Device",          "ro.product.device"),
                ("Chipset",         "ro.hardware"),
            ]
            clear()
            hr(color=C.BLOOD)
            center_text("Samsung Firmware Info", C.ROYAL)
            hr(color=C.BLOOD)
            print()
            for label, prop in props:
                _, val, _ = adb(*prefix, "shell", f"getprop {prop}")
                if val:
                    print(f"  {c(C.BLOOD, label+':'):<28}{c(C.WHITE, val)}")
            pause()

        elif ch == "3":
            _, out, _ = adb(*prefix, "shell", "service call iphonesubinfo 1")
            digits = re.findall(r"'([0-9a-f.]+)'", out)
            imei = "".join(digits).replace(".", "")
            if imei:
                print(f"\n  {c(C.GOLD, 'IMEI:')}  {c(C.WHITE, imei)}")
            else:
                _, out2, _ = adb(*prefix, "shell", "getprop persist.radio.imei")
                print(f"\n  {c(C.GOLD, 'IMEI:')}  {c(C.WHITE, out2 or 'not found — try *#06# on device')}")
            pause()

        elif ch == "4":
            adb(*prefix, "reboot", "download")
            success("rebooting to download mode...")
            pause()

        elif ch == "5":
            dialer_menu()

        elif ch == "6":
            code, out, err = adb(*prefix, "shell", "settings put global adb_enabled 1")
            success("ADB enabled") if code == 0 else error(err)
            pause()

# ══════════════════════════════════════════════════════════════════════════════
#  DIALER TRICKS
# ══════════════════════════════════════════════════════════════════════════════

DIALER_TRICKS = [
    {
        "brand": "Samsung (all — S8+, A-series, Note, Z-series)",
        "codes": ["*#0*#", "*#9900#", "*#1234#"],
        "steps": [
            "Power on device to FRP/setup screen",
            "Tap 'Emergency Call' or swipe to dialer",
            "Dial *#0*# → hardware test menu opens",
            "Back out → semi-accessible state",
            "Dial *#*#4636#*#* → phone info menu",
            "From any open menu → find browser/file manager",
            "Download ADB WiFi APK from browser",
            "Install → enable wireless debugging",
            "Connect from SoulWoRn → run FRP method 2 or 3",
        ],
        "note": "Works Samsung S8–S24. Some regions patched.",
    },
    {
        "brand": "Samsung — TalkBack trick (2022+)",
        "codes": [],
        "steps": [
            "Hold volume up+down 3 seconds → TalkBack activates",
            "Draw L-shape with two fingers → TalkBack menu",
            "Navigate to TalkBack Settings → Help & Feedback",
            "WebView opens → navigate to APK host",
            "Download + install ADB enabler APK",
            "Enable wireless ADB → connect from SoulWoRn",
        ],
        "note": "Patched on some 2023+ firmware but still works widely.",
    },
    {
        "brand": "Google Pixel (3–9)",
        "codes": [],
        "steps": [
            "Connect to WiFi (required for Pixel FRP)",
            "On Google signin: tap text field → long press → Autofill",
            "Or tap Back on keyboard → accessibility settings",
            "Enable TalkBack → navigate to Settings",
            "Enable Developer Options (tap Build Number 7x)",
            "Enable Wireless Debugging",
            "Connect from SoulWoRn → run FRP method 4",
        ],
        "note": "Pixel FRP is tighter — WiFi is mandatory.",
    },
    {
        "brand": "Maxwest / Acer Iconia / Generic MTK",
        "codes": ["*#*#4636#*#*", "*#*#526#*#*"],
        "steps": [
            "Tap Emergency Call on setup screen",
            "Dial *#*#4636#*#* → diagnostics menu on Maxwest",
            "Look for 'Run ping test' → may open browser",
            "Alt: TalkBack L-shape → Help & Feedback WebView",
            "Download ADB WiFi APK via WebView",
            "Enable wireless ADB → SoulWoRn FRP method 7 or 8",
        ],
        "note": "Maxwest Nitro 5C: Android 7.1.1 MTK6580. Very weak FRP.",
    },
    {
        "brand": "Generic Android (2012–2019)",
        "codes": ["*#*#4636#*#*", "*#*#7780#*#*"],
        "steps": [
            "Emergency Call → dial *#*#4636#*#*",
            "Phone info menu on most OEMs",
            "Find any button that opens browser/activity",
            "Download + sideload ADB WiFi APK",
            "Or: put APK on SD card, access via file manager",
            "SoulWoRn FRP method 1 or 6",
        ],
        "note": "Success varies wildly by OEM and year.",
    },
]

def dialer_menu():
    clear()
    hr_double(C.BLOOD)
    center_text("📞  D I A L E R  T R I C K S", C.ROYAL)
    hr_double(C.BLOOD)
    print()
    info("get ADB access on a locked device BEFORE connecting to SoulWoRn")
    print()

    for i, t in enumerate(DIALER_TRICKS, 1):
        print(f"  {c(C.BLOOD, f'[{i}]')}  {c(C.VIOLET, t['brand'])}")
    print(f"  {c(C.BLOOD,'[0]')}  back")
    print()
    ch = input(c(C.ROYAL, "  dialer ❯ ")).strip()
    if ch == "0" or not ch.isdigit(): return
    idx = int(ch) - 1
    if idx < 0 or idx >= len(DIALER_TRICKS): return

    t = DIALER_TRICKS[idx]
    clear()
    hr(color=C.BLOOD)
    center_text(t["brand"], C.ROYAL)
    hr(color=C.BLOOD)

    if t["codes"]:
        print(f"\n  {c(C.GOLD,'dialer codes:')}  {c(C.WHITE, '  ·  '.join(t['codes']))}\n")

    print(c(C.BLOOD, "\n  step by step:\n"))
    for i, step in enumerate(t["steps"], 1):
        print(f"  {c(C.ROYAL, str(i)+'.')}  {c(C.LAVENDER, step)}")
        time.sleep(0.05)

    print(f"\n  {c(C.GOLD, 'note:')}  {c(C.GREY, t['note'])}")
    pause()

# ══════════════════════════════════════════════════════════════════════════════
#  BUILD.PROP EDITOR
# ══════════════════════════════════════════════════════════════════════════════

BUILD_PROP_PATHS = [
    "/system/build.prop",
    "/vendor/build.prop",
    "/product/build.prop",
    "/odm/build.prop",
    "/system_ext/build.prop",
]

SPOOF_PRESETS = {
    "1": {
        "name": "Pixel 9 Pro (Play Integrity / Attestation spoof)",
        "props": {
            "ro.product.model":        "Pixel 9 Pro",
            "ro.product.name":         "caiman",
            "ro.product.device":       "caiman",
            "ro.product.brand":        "google",
            "ro.product.manufacturer": "Google",
            "ro.build.fingerprint":    "google/caiman/caiman:15/AP3A.241005.015/12345678:user/release-keys",
        },
    },
    "2": {
        "name": "Samsung Galaxy S25 Ultra",
        "props": {
            "ro.product.model":        "SM-S938B",
            "ro.product.name":         "e3q",
            "ro.product.device":       "e3q",
            "ro.product.brand":        "samsung",
            "ro.product.manufacturer": "samsung",
        },
    },
    "3": {
        "name": "Hide root (basic props)",
        "props": {
            "ro.debuggable":       "0",
            "ro.secure":           "1",
            "service.adb.root":    "0",
            "ro.build.tags":       "release-keys",
            "ro.build.type":       "user",
        },
    },
    "4": {
        "name": "OnePlus 12 spoof",
        "props": {
            "ro.product.model":        "CPH2573",
            "ro.product.brand":        "OnePlus",
            "ro.product.manufacturer": "OnePlus",
            "ro.product.device":       "waffle",
        },
    },
}

def buildprop_menu(serial=None):
    prefix = ["-s", serial] if serial else []
    while True:
        clear()
        hr_double(C.ROYAL)
        center_text("⚙   B U I L D . P R O P  E D I T O R", C.BLOOD)
        hr_double(C.ROYAL)
        print()
        warn("requires root (su) on target device")
        print()
        print(f"  {c(C.BLOOD,'[1]')}  view partition")
        print(f"  {c(C.BLOOD,'[2]')}  search prop key")
        print(f"  {c(C.BLOOD,'[3]')}  edit / set prop value")
        print(f"  {c(C.BLOOD,'[4]')}  pull to local file")
        print(f"  {c(C.BLOOD,'[5]')}  push local file to device")
        print(f"  {c(C.BLOOD,'[6]')}  spoof presets")
        print(f"  {c(C.BLOOD,'[0]')}  back")
        print()
        ch = input(c(C.ROYAL, "  build.prop ❯ ")).strip()
        if ch == "0": break

        elif ch == "1":
            path = _pick_partition()
            if not path: continue
            _, out, err = adb(*prefix, "shell", f"cat {path}")
            if out:
                lines = out.splitlines()
                clear()
                hr(color=C.BLOOD)
                center_text(f"{path} ({len(lines)} lines)", C.ROYAL)
                hr(color=C.BLOOD)
                for line in lines[:100]:
                    if line.startswith("#"):
                        print(c(C.DIM, f"  {line}"))
                    else:
                        k, _, v = line.partition("=")
                        print(f"  {c(C.BLOOD, k)}={c(C.WHITE, v)}")
                if len(lines) > 100:
                    print(c(C.GREY, f"\n  ... +{len(lines)-100} more (pull file for full view)"))
            else:
                error(f"cannot read {path}: {err}")
            pause()

        elif ch == "2":
            key = input(c(C.WHITE, "  search > ")).strip()
            found = False
            for path in BUILD_PROP_PATHS:
                _, out, _ = adb(*prefix, "shell", f"grep -i '{key}' {path} 2>/dev/null")
                if out:
                    print(c(C.ROYAL, f"\n  ── {path} ──"))
                    for line in out.splitlines():
                        print(f"  {c(C.GOLD, line)}")
                    found = True
            if not found: warn("key not found in any partition")
            pause()

        elif ch == "3":
            path = _pick_partition()
            if not path: continue
            key = input(c(C.WHITE, "  prop key > ")).strip()
            val = input(c(C.WHITE, "  new value > ")).strip()
            spinner("remounting + applying...", 1)
            adb(*prefix, "shell", "su -c 'mount -o remount,rw /system'")
            adb(*prefix, "shell",
                f"su -c \"sed -i 's|^{key}=.*|{key}={val}|' {path}\"")
            _, check, _ = adb(*prefix, "shell", f"grep '^{key}' {path}")
            if key in check:
                success(f"set {key}={val}")
            else:
                adb(*prefix, "shell", f"su -c 'echo \"{key}={val}\" >> {path}'")
                success(f"appended {key}={val}")
            adb(*prefix, "shell", "su -c 'mount -o remount,ro /system'")
            info("reboot to apply")
            pause()

        elif ch == "4":
            path = _pick_partition()
            if not path: continue
            fname = path.replace("/", "_").lstrip("_") + ".txt"
            code, out, err = adb(*prefix, "pull", path, f"./{fname}")
            success(f"saved to ./{fname}") if code == 0 else error(err)
            pause()

        elif ch == "5":
            local = input(c(C.WHITE, "  local file path > ")).strip()
            path  = _pick_partition()
            if not path or not os.path.exists(local): continue
            adb(*prefix, "shell", "su -c 'mount -o remount,rw /system'")
            code, out, err = adb(*prefix, "push", local, path)
            adb(*prefix, "shell", f"su -c 'chmod 644 {path}'")
            adb(*prefix, "shell", "su -c 'mount -o remount,ro /system'")
            success("pushed") if code == 0 else error(err)
            pause()

        elif ch == "6":
            clear()
            hr(color=C.BLOOD)
            center_text("SPOOF PRESETS", C.ROYAL)
            hr(color=C.BLOOD)
            print()
            for k, v in SPOOF_PRESETS.items():
                print(f"  {c(C.BLOOD, f'[{k}]')}  {c(C.VIOLET, v['name'])}")
            print(f"  {c(C.BLOOD,'[0]')}  cancel")
            print()
            pch = input(c(C.ROYAL, "  ❯ ")).strip()
            if pch not in SPOOF_PRESETS: continue
            preset = SPOOF_PRESETS[pch]
            path = _pick_partition()
            if not path: continue
            warn(f"applying: {preset['name']}")
            if not confirm("proceed?"): continue
            spinner("applying preset...", 1)
            adb(*prefix, "shell", "su -c 'mount -o remount,rw /system'")
            for k, v in preset["props"].items():
                adb(*prefix, "shell",
                    f"su -c \"sed -i 's|^{k}=.*|{k}={v}|' {path}\"")
                print(f"  {c(C.GREEN,'✓')}  {c(C.GREY, k)}={c(C.WHITE, v)}")
            adb(*prefix, "shell", "su -c 'mount -o remount,ro /system'")
            success("preset applied — reboot to take effect")
            pause()

def _pick_partition():
    print(c(C.BLOOD, "\n  select partition:"))
    for i, p in enumerate(BUILD_PROP_PATHS, 1):
        print(f"  {c(C.BLOOD, f'[{i}]')}  {c(C.GREY, p)}")
    print(f"  {c(C.BLOOD,'[0]')}  cancel")
    ch = input(c(C.ROYAL, "  ❯ ")).strip()
    if ch == "0" or not ch.isdigit(): return None
    idx = int(ch) - 1
    return BUILD_PROP_PATHS[idx] if 0 <= idx < len(BUILD_PROP_PATHS) else None

# ══════════════════════════════════════════════════════════════════════════════
#  EFS WIPE
# ══════════════════════════════════════════════════════════════════════════════

EFS_FRP_PATHS = [
    "/efs/Factory/a",
    "/efs/FactoryApp/a",
    "/efs/FactoryApp/b",
    "/mnt/vendor/efs/FactoryApp/a",
    "/mnt/vendor/efs/FactoryApp/b",
    "/efs/FactoryApp/keydata",
    "/efs/FactoryApp/keydata.bak",
]

def efs_menu(serial=None):
    prefix = ["-s", serial] if serial else []
    while True:
        clear()
        hr_double(C.BLOOD)
        center_text("🧬  E F S  W I P E  ·  S A M S U N G", C.ROYAL)
        hr_double(C.BLOOD)
        print()
        info("EFS stores Samsung FRP account binding — clearing removes Google lock")
        warn("requires root OR recovery context")
        print()
        print(f"  {c(C.BLOOD,'[1]')}  scan EFS paths")
        print(f"  {c(C.BLOOD,'[2]')}  wipe EFS FRP files  {c(C.GREY,'(needs root)')}")
        print(f"  {c(C.BLOOD,'[3]')}  build EFS wipe sideload zip")
        print(f"  {c(C.BLOOD,'[0]')}  back")
        print()
        ch = input(c(C.ROYAL, "  efs ❯ ")).strip()
        if ch == "0": break

        elif ch == "1":
            spinner("scanning EFS...", 1)
            found = 0
            for path in EFS_FRP_PATHS:
                code, out, _ = adb(*prefix, "shell",
                    f"ls -la {path} 2>/dev/null && echo EXISTS")
                if "EXISTS" in out:
                    print(f"  {c(C.GREEN,'✓')}  {c(C.WHITE, path)}")
                    found += 1
                else:
                    print(f"  {c(C.DIM,'–')}  {c(C.DIM, path)}")
            print()
            info(f"{found} EFS FRP paths found")
            pause()

        elif ch == "2":
            warn("this requires root (su) on the device")
            if not confirm("proceed?"): continue
            wiped = 0
            for path in EFS_FRP_PATHS:
                code, out, _ = adb(*prefix, "shell",
                    f"su -c 'echo \"\" > {path} && echo WIPED' 2>/dev/null")
                if "WIPED" in out:
                    print(f"  {c(C.GREEN,'✓')}  {c(C.GREY, path)}")
                    wiped += 1
                else:
                    print(f"  {c(C.DIM,'–')}  {c(C.DIM, path)}")
            success(f"{wiped} files wiped — reboot to apply")
            pause()

        elif ch == "3":
            import zipfile as _zip
            efs_cmds = "\n".join([
                f'  [ -e "{p}" ] && echo "" > "{p}" '
                f'&& ui_print ">> wiped: {p}"'
                for p in EFS_FRP_PATHS
            ])
            binary = f"""#!/sbin/sh
OUTFD=$2
ui_print() {{ echo "ui_print $1" >> /proc/self/fd/$OUTFD; echo "ui_print " >> /proc/self/fd/$OUTFD; }}
set_progress() {{ echo "set_progress $1" >> /proc/self/fd/$OUTFD; }}
ui_print "=============================="
ui_print "  SoulWoRn EFS Wipe"
ui_print "  Samsung — all variants"
ui_print "=============================="
set_progress 0.2
{efs_cmds}
set_progress 0.7
for c in /dev/block/by-name/frp /dev/block/bootdevice/by-name/frp; do
  [ -e "$c" ] && dd if=/dev/zero of="$c" bs=512 count=256 2>/dev/null && ui_print ">> $c zeroed"
done
set_progress 1.0
ui_print "DONE — Reboot system now"
"""
            zip_path = os.path.expanduser("~/downloads/soulworn_efs_wipe.zip")
            os.makedirs(os.path.dirname(zip_path), exist_ok=True)
            with _zip.ZipFile(zip_path, "w", _zip.ZIP_DEFLATED) as zf:
                info_z = _zip.ZipInfo("META-INF/com/google/android/update-binary")
                info_z.external_attr = 0o755 << 16
                zf.writestr(info_z, binary)
                zf.writestr("META-INF/com/google/android/updater-script",
                            'ui_print("SoulWoRn EFS wipe");')
            success(f"built: {zip_path}")
            info(f"sideload: adb sideload {zip_path}")
            pause()

# ══════════════════════════════════════════════════════════════════════════════
#  SIDELOAD ZIP BUILDER
# ══════════════════════════════════════════════════════════════════════════════

def zip_builder_menu(serial=None):
    import zipfile as _zip
    clear()
    hr_double(C.BLOOD)
    center_text("📦  S I D E L O A D  Z I P  B U I L D E R", C.ROYAL)
    hr_double(C.BLOOD)
    print()

    # auto-fill from device
    d = {"model": "Unknown", "codename": "generic", "android": "?",
         "patch": "?", "build": "?", "brand": "Unknown"}
    if serial:
        spinner("reading device info...", 1)
        nfo = get_device_info(serial)
        d = {
            "model":    nfo.get("Model", "Unknown"),
            "codename": nfo.get("Codename", "generic"),
            "android":  nfo.get("Android", "?"),
            "patch":    nfo.get("Patch", "?"),
            "build":    nfo.get("Build", "?"),
            "brand":    nfo.get("Brand", "Unknown"),
        }

    print(f"  target: {c(C.GOLD, d['model'])} / {c(C.ROYAL, d['codename'])}")
    print(f"  android: {c(C.WHITE, d['android'])} · patch: {c(C.WHITE, d['patch'])}")
    print()
    print(f"  {c(C.BLOOD,'[1]')}  FRP clear + flags")
    print(f"  {c(C.BLOOD,'[2]')}  FRP + EFS wipe (Samsung deep)")
    print(f"  {c(C.BLOOD,'[3]')}  setup flags only (no partition wipe)")
    print(f"  {c(C.BLOOD,'[4]')}  custom commands")
    print(f"  {c(C.BLOOD,'[0]')}  cancel")
    print()
    ch = input(c(C.ROYAL, "  zip-type ❯ ")).strip()
    if ch == "0": return

    custom_cmds = ""
    if ch == "4":
        print(c(C.LAVENDER, "  enter commands one per line · blank to finish:"))
        lines = []
        while True:
            ln = input("  cmd> ").strip()
            if not ln: break
            lines.append(ln)
        custom_cmds = "\n".join([
            f'run_program("/sbin/sh","-c","{l}");' for l in lines
        ])

    efs_block = ""
    if ch == "2":
        efs_block = "\n".join([
            f'  [ -e "{p}" ] && echo "" > "{p}" '
            f'&& ui_print ">> wiped: {p}"'
            for p in EFS_FRP_PATHS
        ])

    frp_wipe = ch in ("1", "2")
    flags_only = ch == "3"

    binary = f"""#!/sbin/sh
# SoulWoRn Sideload ZIP
# {d['model']} / {d['codename']}
# Android {d['android']} · Patch {d['patch']}
OUTFD=$2
ZIP=$3
ui_print() {{ echo "ui_print $1" >> /proc/self/fd/$OUTFD; echo "ui_print " >> /proc/self/fd/$OUTFD; }}
set_progress() {{ echo "set_progress $1" >> /proc/self/fd/$OUTFD; }}
ui_print "=============================="
ui_print "  SoulWoRn FRP Clear"
ui_print "  {d['model']} / {d['codename']}"
ui_print "  Android {d['android']}"
ui_print "=============================="
set_progress 0.1
{"" if flags_only else '''
FRP_BLOCK=""
for c in /dev/block/by-name/frp /dev/block/bootdevice/by-name/frp; do
  [ -e "$c" ] && FRP_BLOCK="$c" && break
done
[ -z "$FRP_BLOCK" ] && FRP_BLOCK=$(find /dev/block/platform -name "frp" 2>/dev/null | head -1)
if [ -n "$FRP_BLOCK" ]; then
  dd if=/dev/zero of="$FRP_BLOCK" bs=512 count=256 2>/dev/null
  ui_print ">> FRP partition cleared"
fi
'''}
set_progress 0.4
mount /data 2>/dev/null
if mount | grep -q " /data "; then
  DB="/data/data/com.google.android.providers.settings/databases/settings.db"
  [ -f "$DB" ] && sqlite3 "$DB" \\
    "INSERT OR REPLACE INTO secure(name,value) VALUES('user_setup_complete','1');" 2>/dev/null
  for f in /data/system/users/0/settings_secure.xml; do
    [ -f "$f" ] && sed -i 's/frp_credential_enabled" value="1"/frp_credential_enabled" value="0"/g' "$f" 2>/dev/null
  done
  ui_print ">> setup flags written"
fi
set_progress 0.7
{efs_block}
{custom_cmds}
set_progress 1.0
ui_print "=============================="
ui_print "  DONE — Reboot system now"
ui_print "=============================="
"""

    safe = re.sub(r"[^\w\-]", "_", d["model"])
    zip_name = f"soulworn_frp_{safe}_{d['codename']}.zip"
    zip_path = os.path.join(os.path.expanduser("~/downloads"), zip_name)
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)

    spinner(f"building {zip_name}...", 1)
    with _zip.ZipFile(zip_path, "w", _zip.ZIP_DEFLATED) as zf:
        info_z = _zip.ZipInfo("META-INF/com/google/android/update-binary")
        info_z.external_attr = 0o755 << 16
        zf.writestr(info_z, binary)
        zf.writestr("META-INF/com/google/android/updater-script",
                    f'ui_print("SoulWoRn sideload — {d["model"]}");')

    md5  = hashlib.md5(open(zip_path,"rb").read()).hexdigest()
    size = os.path.getsize(zip_path)

    success(f"built: {zip_path}")
    print(f"  {c(C.GOLD,'size:')}  {size:,} bytes")
    print(f"  {c(C.GOLD,'md5:')}   {md5}")
    print()
    hr(color=C.ROYAL)
    print(c(C.BLOOD, "\n  SIDELOAD COMMAND:"))
    typewrite(f"  adb sideload {zip_path}", C.GREEN, 0.02)
    info("select 'Apply update from ADB' in recovery first")
    hr(color=C.ROYAL)
    pause()

# ══════════════════════════════════════════════════════════════════════════════
#  HASH / INTEGRITY TOOLS
# ══════════════════════════════════════════════════════════════════════════════

def hash_menu(serial=None):
    prefix = ["-s", serial] if serial else []
    while True:
        clear()
        hr_double(C.ROYAL)
        center_text("#  H A S H  ·  I N T E G R I T Y", C.BLOOD)
        hr_double(C.ROYAL)
        print()
        print(f"  {c(C.BLOOD,'[1]')}  hash local file  (MD5/SHA1/SHA256)")
        print(f"  {c(C.BLOOD,'[2]')}  hash device file")
        print(f"  {c(C.BLOOD,'[3]')}  compare local vs device")
        print(f"  {c(C.BLOOD,'[4]')}  pull + verify from device")
        print(f"  {c(C.BLOOD,'[5]')}  hash all files in directory")
        print(f"  {c(C.BLOOD,'[6]')}  APK integrity check")
        print(f"  {c(C.BLOOD,'[0]')}  back")
        print()
        ch = input(c(C.ROYAL, "  hash ❯ ")).strip()
        if ch == "0": break

        elif ch == "1":
            path = input(c(C.WHITE, "  local file > ")).strip()
            if os.path.exists(path):
                print()
                for algo in ["md5", "sha1", "sha256"]:
                    h = _hash_file(path, algo)
                    print(f"  {c(C.BLOOD, algo.upper()+':'):<16}{c(C.WHITE, h)}")
                print(f"  {c(C.BLOOD,'SIZE:'):<16}{c(C.WHITE, f'{os.path.getsize(path):,} bytes')}")
            else:
                error("file not found")
            pause()

        elif ch == "2":
            path = input(c(C.WHITE, "  device path > ")).strip()
            for algo, cmd in [("MD5","md5sum"),("SHA1","sha1sum"),("SHA256","sha256sum")]:
                _, out, _ = adb(*prefix, "shell", f"{cmd} {path}")
                if out:
                    print(f"  {c(C.BLOOD, algo+':'):<16}{c(C.WHITE, out.split()[0])}")
            pause()

        elif ch == "3":
            local  = input(c(C.WHITE, "  local file > ")).strip()
            remote = input(c(C.WHITE, "  device path > ")).strip()
            if not os.path.exists(local):
                error("local file not found"); pause(); continue
            lmd5 = _hash_file(local, "md5")
            _, out, _ = adb(*prefix, "shell", f"md5sum {remote}")
            rmd5 = out.split()[0] if out else None
            print(f"\n  {c(C.BLOOD,'local:')}   {lmd5}")
            print(f"  {c(C.BLOOD,'device:')}  {rmd5 or 'failed'}")
            if lmd5 and rmd5:
                if lmd5 == rmd5: success("MATCH — files identical")
                else: error("MISMATCH — files differ")
            pause()

        elif ch == "4":
            remote = input(c(C.WHITE, "  device path > ")).strip()
            fname  = os.path.basename(remote)
            spinner(f"pulling {fname}...", 1)
            code, _, err = adb(*prefix, "pull", remote, f"./{fname}")
            if code == 0:
                lmd5 = _hash_file(f"./{fname}", "md5")
                _, out, _ = adb(*prefix, "shell", f"md5sum {remote}")
                rmd5 = out.split()[0] if out else None
                print(f"\n  {c(C.BLOOD,'local:')}   {lmd5}")
                print(f"  {c(C.BLOOD,'device:')}  {rmd5 or '?'}")
                if lmd5 == rmd5: success(f"verified — saved ./{fname}")
                else: error("hash mismatch after pull!!")
            else:
                error(f"pull failed: {err}")
            pause()

        elif ch == "5":
            dirpath = input(c(C.WHITE, "  directory > ")).strip() or "."
            if os.path.isdir(dirpath):
                files = sorted([f for f in os.listdir(dirpath)
                                if os.path.isfile(os.path.join(dirpath, f))])
                clear()
                hr(color=C.BLOOD)
                for fname in files:
                    full = os.path.join(dirpath, fname)
                    md5  = _hash_file(full, "md5")
                    sha1 = _hash_file(full, "sha1")
                    print(f"  {c(C.VIOLET, fname)}")
                    print(f"    {c(C.GREY,'MD5:')}   {md5}")
                    print(f"    {c(C.GREY,'SHA1:')}  {sha1}")
            else:
                error("directory not found")
            pause()

        elif ch == "6":
            apk = input(c(C.WHITE, "  APK path > ")).strip()
            if not os.path.exists(apk):
                error("not found"); pause(); continue
            print(f"\n  {c(C.BLOOD,'APK:')}     {apk}")
            print(f"  {c(C.BLOOD,'size:')}    {os.path.getsize(apk):,} bytes")
            print(f"  {c(C.BLOOD,'MD5:')}     {_hash_file(apk,'md5')}")
            print(f"  {c(C.BLOOD,'SHA256:')} {_hash_file(apk,'sha256')}")
            if shutil.which("apksigner"):
                r = subprocess.run(["apksigner","verify","--print-certs",apk],
                                   capture_output=True, text=True)
                if r.stdout:
                    print(c(C.ROYAL, "\n  cert info:"))
                    for line in r.stdout.splitlines()[:8]:
                        print(c(C.GREY, f"  {line}"))
            pause()

def _hash_file(path, algo="md5"):
    try:
        h = hashlib.new(algo)
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""): h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return f"error:{e}"

# ══════════════════════════════════════════════════════════════════════════════
#  ADVANCED TOOLS
# ══════════════════════════════════════════════════════════════════════════════

def advanced_menu(serial=None):
    prefix = ["-s", serial] if serial else []
    while True:
        clear()
        hr_double(C.BLOOD)
        center_text("⚡  A D V A N C E D  T O O L S", C.ROYAL)
        hr_double(C.BLOOD)
        print()
        tools = [
            ("1",  "APK install to device"),
            ("2",  "pull file from device"),
            ("3",  "push file to device"),
            ("4",  "screenshot"),
            ("5",  "grant / revoke permission"),
            ("6",  "enable OEM unlock flag"),
            ("7",  "enable USB debugging via ADB"),
            ("8",  "custom adb shell command"),
            ("9",  "logcat (live · Ctrl+C stop)"),
            ("10", "reboot menu"),
            ("11", "device uptime + battery"),
            ("12", "list running processes"),
            ("13", "clear app data"),
            ("14", "force-stop app"),
            ("15", "set fake battery %"),
        ]
        for num, name in tools:
            print(f"  {c(C.BLOOD, f'[{num}]'):<18}{c(C.LAVENDER, name)}")
        print()
        print(f"  {c(C.BLOOD,'[0]')}  back")
        print()
        ch = input(c(C.ROYAL, "  adv ❯ ")).strip()
        if ch == "0": break

        elif ch == "1":
            apk = input(c(C.WHITE, "  APK path > ")).strip()
            if os.path.exists(apk):
                spinner("installing...", 1)
                code, out, err = adb(*prefix, "install", "-r", apk)
                success(out) if "Success" in out else error(out or err)
            else: error("file not found")
            pause()

        elif ch == "2":
            src  = input(c(C.WHITE, "  device path > ")).strip()
            dest = input(c(C.WHITE, "  local dest (blank=.) > ")).strip() or "."
            spinner("pulling...", 0.5)
            code, out, err = adb(*prefix, "pull", src, dest)
            success(out) if code == 0 else error(err)
            pause()

        elif ch == "3":
            src  = input(c(C.WHITE, "  local file > ")).strip()
            dest = input(c(C.WHITE, "  device dest > ")).strip()
            spinner("pushing...", 0.5)
            code, out, err = adb(*prefix, "push", src, dest)
            success(out) if code == 0 else error(err)
            pause()

        elif ch == "4":
            fname = f"sw_screen_{int(time.time())}.png"
            spinner("capturing...", 0.8)
            adb(*prefix, "shell", f"screencap -p /sdcard/{fname}")
            code, out, err = adb(*prefix, "pull", f"/sdcard/{fname}", f"./{fname}")
            adb(*prefix, "shell", f"rm /sdcard/{fname}")
            success(f"saved: ./{fname}") if code == 0 else error(err)
            pause()

        elif ch == "5":
            pkg  = input(c(C.WHITE, "  package > ")).strip()
            perm = input(c(C.WHITE, "  permission (e.g. android.permission.CAMERA) > ")).strip()
            act  = input(c(C.WHITE, "  grant or revoke? [g/r] > ")).strip().lower()
            cmd  = "grant" if act == "g" else "revoke"
            code, out, err = adb(*prefix, "shell", f"pm {cmd} {pkg} {perm}")
            success(f"{cmd}: {perm}") if code == 0 else error(err)
            pause()

        elif ch == "6":
            code, out, err = adb(*prefix, "shell",
                "settings put global oem_unlock_allowed 1")
            success("OEM unlock flag set — reboot to apply") if code == 0 else error(err)
            pause()

        elif ch == "7":
            code, out, err = adb(*prefix, "shell",
                "settings put global adb_enabled 1")
            success("ADB enabled") if code == 0 else error(err)
            pause()

        elif ch == "8":
            cmd = input(c(C.WHITE, "  adb shell ❯ ")).strip()
            _, out, err = adb(*prefix, "shell", cmd)
            print()
            hr(color=C.ROYAL)
            print(c(C.WHITE, out or err or "(no output)"))
            hr(color=C.ROYAL)
            pause()

        elif ch == "9":
            print(c(C.DIM, "\n  logcat live — Ctrl+C to stop\n"))
            try:
                subprocess.run(["adb"] + prefix + ["logcat", "-v", "brief"])
            except KeyboardInterrupt:
                pass
            pause()

        elif ch == "10":
            _reboot_menu(prefix)

        elif ch == "11":
            _, uptime, _ = adb(*prefix, "shell", "uptime")
            _, batt,   _ = adb(*prefix, "shell",
                "dumpsys battery | grep -E 'level|status|temperature'")
            print(f"\n  {c(C.GOLD,'uptime:')}  {uptime}")
            print(c(C.GOLD, "\n  battery:"))
            for line in batt.splitlines():
                print(c(C.WHITE, f"    {line.strip()}"))
            pause()

        elif ch == "12":
            _, out, _ = adb(*prefix, "shell", "ps -A 2>/dev/null | head -40")
            clear()
            hr(color=C.BLOOD)
            print(c(C.LAVENDER, out))
            hr(color=C.BLOOD)
            pause()

        elif ch == "13":
            pkg = input(c(C.WHITE, "  package to clear > ")).strip()
            code, out, err = adb(*prefix, "shell", f"pm clear {pkg}")
            success(out) if "Success" in out else error(out or err)
            pause()

        elif ch == "14":
            pkg = input(c(C.WHITE, "  package to stop > ")).strip()
            code, out, err = adb(*prefix, "shell", f"am force-stop {pkg}")
            success(f"force-stopped {pkg}") if code == 0 else error(err)
            pause()

        elif ch == "15":
            val = input(c(C.WHITE, "  battery % (1-100) > ")).strip()
            adb(*prefix, "shell", f"dumpsys battery set level {val}")
            success(f"fake battery set to {val}%")
            info("reset with: adb shell dumpsys battery reset")
            pause()

def _reboot_menu(prefix):
    clear()
    hr(color=C.BLOOD)
    center_text("REBOOT", C.ROYAL)
    hr(color=C.BLOOD)
    print()
    options = [
        ("1", "Normal",           ["reboot"]),
        ("2", "Recovery",         ["reboot", "recovery"]),
        ("3", "Bootloader",       ["reboot", "bootloader"]),
        ("4", "Download Mode",    ["reboot", "download"]),
        ("5", "Power Off",        ["shell", "reboot", "-p"]),
        ("6", "Soft reboot",      ["shell", "setprop ctl.restart zygote"]),
    ]
    for num, name, _ in options:
        print(f"  {c(C.BLOOD, f'[{num}]')}  {c(C.LAVENDER, name)}")
    print(f"  {c(C.BLOOD,'[0]')}  cancel")
    print()
    ch = input(c(C.ROYAL, "  reboot ❯ ")).strip()
    for num, name, args in options:
        if ch == num:
            adb(*prefix, *args)
            success(f"rebooting → {name}")
            break
    pause()

# ══════════════════════════════════════════════════════════════════════════════
#  DEVICE PROFILES DB
# ══════════════════════════════════════════════════════════════════════════════

DEVICE_PROFILES = {
    # Samsung
    "o1q":     {"name": "Samsung Galaxy S21",       "frp": ["2","3"], "bloat": "samsung", "efs": True},
    "t2q":     {"name": "Samsung Galaxy S21+",      "frp": ["2","3"], "bloat": "samsung", "efs": True},
    "p3q":     {"name": "Samsung Galaxy S21 Ultra", "frp": ["2","3"], "bloat": "samsung", "efs": True},
    "r0q":     {"name": "Samsung Galaxy S22",       "frp": ["3"],     "bloat": "samsung", "efs": True},
    "b0q":     {"name": "Samsung Galaxy S22 Ultra", "frp": ["3"],     "bloat": "samsung", "efs": True},
    "dm1q":    {"name": "Samsung Galaxy S23",       "frp": ["3","6"], "bloat": "samsung", "efs": True},
    "dm3q":    {"name": "Samsung Galaxy S23 Ultra", "frp": ["3","6"], "bloat": "samsung", "efs": True},
    "zq":      {"name": "Samsung Galaxy S20",       "frp": ["2"],     "bloat": "samsung", "efs": True},
    "beyond1": {"name": "Samsung Galaxy S10",       "frp": ["1","2"], "bloat": "samsung", "efs": True},
    "beyond2": {"name": "Samsung Galaxy S10+",      "frp": ["1","2"], "bloat": "samsung", "efs": True},
    "crownq":  {"name": "Samsung Galaxy Note 20",   "frp": ["2","3"], "bloat": "samsung", "efs": True},
    "a52q":    {"name": "Samsung Galaxy A52",       "frp": ["2","3"], "bloat": "samsung", "efs": True},
    # Pixels
    "panther": {"name": "Google Pixel 7",           "frp": ["4"],     "bloat": "google_pixel", "efs": False},
    "cheetah": {"name": "Google Pixel 7 Pro",       "frp": ["4"],     "bloat": "google_pixel", "efs": False},
    "oriole":  {"name": "Google Pixel 6",           "frp": ["4"],     "bloat": "google_pixel", "efs": False},
    "raven":   {"name": "Google Pixel 6 Pro",       "frp": ["4"],     "bloat": "google_pixel", "efs": False},
    "shiba":   {"name": "Google Pixel 8",           "frp": ["4"],     "bloat": "google_pixel", "efs": False},
    "caiman":  {"name": "Google Pixel 9 Pro",       "frp": ["4"],     "bloat": "google_pixel", "efs": False},
    "flame":   {"name": "Google Pixel 4",           "frp": ["4"],     "bloat": "google_pixel", "efs": False},
    "redfin":  {"name": "Google Pixel 5",           "frp": ["4"],     "bloat": "google_pixel", "efs": False},
    # Maxwest / Budget
    "nitro5c": {"name": "Maxwest Nitro 5C",         "frp": ["1","7","8"], "bloat": "generic", "efs": False},
    "nitro5m": {"name": "Maxwest Nitro 5M",         "frp": ["1","7","8"], "bloat": "generic", "efs": False},
    "mt6580":  {"name": "Generic MTK MT6580",       "frp": ["1","8"], "bloat": "generic", "efs": False},
    "mt6739":  {"name": "Generic MTK MT6739",       "frp": ["1","8"], "bloat": "generic", "efs": False},
    "mt6765":  {"name": "Generic MTK MT6765",       "frp": ["1","8"], "bloat": "generic", "efs": False},
}

def autodetect_menu(serial=None):
    clear()
    hr_double(C.BLOOD)
    center_text("🔍  A U T O  D E V I C E  P R O F I L E", C.ROYAL)
    hr_double(C.BLOOD)
    print()
    spinner("scanning device...", 1.5)

    prefix = ["-s", serial] if serial else []
    _, codename, _ = adb(*prefix, "shell", "getprop ro.product.device")
    nfo = get_device_info(serial)
    codename = codename.lower().strip()
    profile  = DEVICE_PROFILES.get(codename)

    print()
    for k, v in nfo.items():
        print(f"  {c(C.BLOOD, k+':'):<28}{c(C.WHITE, v)}")
    print()

    if profile:
        hr(color=C.ROYAL)
        typewrite(f"  ★  known device: {profile['name']}", C.GOLD, 0.02)
        print()
        print(f"  {c(C.BLOOD,'recommended FRP:')}  {c(C.WHITE, ', '.join(profile['frp']))}")
        print(f"  {c(C.BLOOD,'bloat profile:')}    {c(C.WHITE, profile['bloat'])}")
        if profile["efs"]:
            print(f"  {c(C.BLOOD,'EFS wipe:')}         {c(C.GREEN,'supported')}")
        hr(color=C.ROYAL)
        print()
        print(f"  {c(C.BLOOD,'[1]')}  run recommended FRP now")
        print(f"  {c(C.BLOOD,'[2]')}  build sideload zip")
        print(f"  {c(C.BLOOD,'[3]')}  remove bloat")
        if profile["efs"]:
            print(f"  {c(C.BLOOD,'[4]')}  EFS wipe")
        print(f"  {c(C.BLOOD,'[0]')}  back")
        print()
        ch = input(c(C.ROYAL, "  ❯ ")).strip()
        if ch == "1": frp_menu(serial)
        elif ch == "2": zip_builder_menu(serial)
        elif ch == "3": bloat_menu(serial)
        elif ch == "4" and profile["efs"]: efs_menu(serial)
    else:
        warn(f"unknown codename '{codename}' — not in profile DB")
        print()
        print(f"  {c(C.BLOOD,'[1]')}  try generic FRP (method 1 + 6)")
        print(f"  {c(C.BLOOD,'[2]')}  build generic sideload zip")
        print(f"  {c(C.BLOOD,'[0]')}  back")
        print()
        ch = input(c(C.ROYAL, "  ❯ ")).strip()
        if ch == "1": frp_menu(serial)
        elif ch == "2": zip_builder_menu(serial)

    pause()

# ══════════════════════════════════════════════════════════════════════════════
#  DEPENDENCY CHECK
# ══════════════════════════════════════════════════════════════════════════════

def check_deps():
    missing = []
    if not shutil.which("adb"):      missing.append("adb      → pkg install android-tools")
    if not shutil.which("fastboot"): missing.append("fastboot → pkg install android-tools")
    return missing

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN CLI LOOP
# ══════════════════════════════════════════════════════════════════════════════

def cli_main():
    random.seed(os.getpid())

    # dep check
    missing = check_deps()

    serial = None

    while True:
        clear()

        # art
        print(get_art())
        print(get_filler())

        # subtitle
        w = term_width()
        sub = "Samsung S8+ · Pixels · MTK · Any Android 2012+  ·  NO telemetry · v5"
        print(c(C.ROYAL, sub.center(w)))
        print()

        # dep warnings
        if missing:
            for m in missing:
                warn(m)
            print()

        # device status
        if serial:
            print(c(C.GREEN, f"  ● connected: {serial}"))
        else:
            devs = get_devices()
            if devs:
                print(c(C.GOLD, f"  ● {len(devs)} device(s) found — select with [1]"))
            else:
                print(c(C.GREY, "  ○ no devices"))
        print()

        # AI status
        ak = _load_key(KEY_FILE)
        gk = _load_key(GROQ_KEY_FILE)
        ai_status = (
            c(C.GREEN, "claude") if ak else
            c(C.VIOLET, "groq") if gk else
            c(C.GREY, "offline")
        )
        print(c(C.DIM, f"  ghosteey: {ai_status}"))
        print()

        # menu
        hr(char="─", color=C.BLOOD)
        menu = [
            ("1",  "select / change device"),
            ("2",  "auto device profile",     "detect + suggest actions"),
            ("3",  "device info"),
            ("4",  "FRP bypass",              "8 methods"),
            ("5",  "dialer entry tricks",     "ADB entry on locked device"),
            ("6",  "bloatware removal"),
            ("7",  "wireless ADB"),
            ("8",  "samsung tools",           "WLANTEST · EFS · IMEI"),
            ("9",  "sideload zip builder"),
            ("e",  "EFS wipe",                "Samsung FRP account · recovery/root"),
            ("b",  "build.prop editor",       "spoof presets · requires root"),
            ("h",  "hash / MD5 / integrity"),
            ("a",  "advanced tools"),
            ("g",  "ghosteey AI",             "triple fallback · claude/groq/ollama"),
            ("k",  "AI key management"),
            ("q",  "quit"),
        ]
        for item in menu:
            key  = item[0]
            name = item[1]
            hint = item[2] if len(item) > 2 else ""
            kc   = c(C.BLOOD, f"  [{key}]")
            nc   = c(C.WHITE, name)
            hc   = c(C.DIM, f"  {hint}") if hint else ""
            print(f"{kc}  {nc}{hc}")

        hr(char="─", color=C.BLOOD)
        print()

        try:
            ch = input(c(C.ROYAL, "  SoulWoRn ❯ ") + C.WHITE).strip().lower()
        except (KeyboardInterrupt, EOFError):
            break

        if ch == "q":
            clear()
            typewrite("\n  👽 SoulWoRn signing off...\n", C.VIOLET, 0.03)
            break
        elif ch == "1":  serial = select_device()
        elif ch == "2":  autodetect_menu(serial)
        elif ch == "3":  info_menu(serial)
        elif ch == "4":  frp_menu(serial)
        elif ch == "5":  dialer_menu()
        elif ch == "6":  bloat_menu(serial)
        elif ch == "7":  wireless_menu(serial)
        elif ch == "8":  samsung_menu(serial)
        elif ch == "9":  zip_builder_menu(serial)
        elif ch == "e":  efs_menu(serial)
        elif ch == "b":  buildprop_menu(serial)
        elif ch == "h":  hash_menu(serial)
        elif ch == "a":  advanced_menu(serial)
        elif ch == "g":  ghosteey_chat_session(serial)
        elif ch == "k":  _manage_ai_keys()


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    cli_main()
