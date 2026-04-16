#!/bin/bash
# ╔══════════════════════════════════════════════════════════════════╗
# ║         SoulWoRn — UserLAnd Kali Setup Script                   ║
# ║         Samsung S25 · 1080x1920 · bVNC ready                    ║
# ║         run inside UserLAnd Kali terminal                        ║
# ║         NO telemetry · GPL-3.0 · nofatchicks                    ║
# ╚══════════════════════════════════════════════════════════════════╝
# USAGE:
#   bash soulworn_setup.sh
# ─────────────────────────────────────────────────────────────────────

set -uo pipefail

# ── colours ──────────────────────────────────────────────────────────────────
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
CYAN='\033[96m'
MAGENTA='\033[95m'
WHITE='\033[97m'
DIM='\033[2m'
BOLD='\033[1m'
RESET='\033[0m'

# ── logging ───────────────────────────────────────────────────────────────────
LOGFILE="/tmp/soulworn_setup.log"
touch "$LOGFILE"

log()     { echo -e "${GREEN}  ✓${RESET}  $1" | tee -a "$LOGFILE"; }
info()    { echo -e "${CYAN}  ──${RESET}  $1" | tee -a "$LOGFILE"; }
warn()    { echo -e "${YELLOW}  ⚠${RESET}   $1" | tee -a "$LOGFILE"; }
fail()    { echo -e "${RED}  ✗${RESET}  $1" | tee -a "$LOGFILE"; }
sep()     { echo -e "${DIM}  ────────────────────────────────────────${RESET}"; }
section() { echo -e "\n${BOLD}${MAGENTA}  [$1]${RESET}\n"; }

ERRORS=()
soft_fail() { warn "$1 — non-fatal, continuing"; ERRORS+=("$1"); }

# ── apt helper ────────────────────────────────────────────────────────────────
apt_install() {
    local desc="$1"; shift
    info "installing: $desc"
    if apt-get install -y -qq "$@" >> "$LOGFILE" 2>&1; then
        log "$desc OK"
    else
        warn "$desc — retrying individually..."
        for pkg in "$@"; do
            apt-get install -y -qq "$pkg" >> "$LOGFILE" 2>&1 \
                && log "  ✓ $pkg" \
                || soft_fail "  ✗ $pkg skipped"
        done
    fi
}

# ── banner ────────────────────────────────────────────────────────────────────
clear
echo -e "${CYAN}"
cat << 'BANNER'
  ██████╗  ██████╗ ██╗   ██╗██╗     ██╗    ██╗ ██████╗ ██████╗ ███╗   ██╗
  ██╔════╝ ██╔═══██╗██║   ██║██║     ██║    ██║██╔═══██╗██╔══██╗████╗  ██║
  ███████╗ ██║   ██║██║   ██║██║     ██║ █╗ ██║██║   ██║██████╔╝██╔██╗ ██║
  ╚════██║ ██║   ██║██║   ██║██║     ██║███╗██║██║   ██║██╔══██╗██║╚██╗██║
  ███████║ ╚██████╔╝╚██████╔╝███████╗╚███╔███╔╝╚██████╔╝██║  ██║██║ ╚████║
  ╚══════╝  ╚═════╝  ╚═════╝ ╚══════╝ ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝
  UserLAnd Kali Setup · Samsung S25 · bVNC 1080x1920 · nofatchicks 👽
BANNER
echo -e "${RESET}"
echo -e "  ${DIM}log → $LOGFILE${RESET}\n"

# ── sanity ────────────────────────────────────────────────────────────────────
section "SANITY CHECKS"

# internet check
info "checking internet..."
if curl -s --max-time 6 https://kali.org > /dev/null 2>&1; then
    log "internet OK"
else
    warn "no internet — fixing DNS..."
    echo "nameserver 8.8.8.8" > /etc/resolv.conf
    echo "nameserver 1.1.1.1" >> /etc/resolv.conf
    curl -s --max-time 8 https://kali.org > /dev/null 2>&1 \
        && log "internet OK after DNS fix" \
        || { fail "still no internet!!"; read -p "  continue anyway? [y/N] " c; [[ "$c" != "y" ]] && exit 1; }
fi

# disk check
FREE=$(df / --output=avail -m 2>/dev/null | tail -1 | tr -d ' ')
[ -n "$FREE" ] && [ "$FREE" -lt 1500 ] \
    && warn "low disk: ${FREE}MB — may fail" \
    || log "disk: ${FREE:-?}MB free"
sep

# ── update ────────────────────────────────────────────────────────────────────
section "PACKAGE UPDATE"
info "updating package lists..."
apt-get update -qq >> "$LOGFILE" 2>&1 \
    && log "updated" \
    || { apt-get update --fix-missing -qq >> "$LOGFILE" 2>&1; soft_fail "update partial"; }
sep

# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 1 — CORE TOOLS
# ══════════════════════════════════════════════════════════════════════════════
section "PHASE 1 — CORE TOOLS"

apt_install "core utils" \
    curl wget git nano vim \
    python3 python3-pip \
    unzip zip \
    net-tools iproute2 \
    iputils-ping dnsutils \
    netcat-openbsd socat \
    htop tmux screen \
    ca-certificates openssl \
    lsof procps file less tree
sep

# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 2 — PYTHON DEPS
# ══════════════════════════════════════════════════════════════════════════════
section "PHASE 2 — PYTHON DEPS"

apt_install "Python Qt5" \
    python3-pyqt5 \
    python3-pyqt5.qtsvg

info "installing pip packages..."
pip3 install --quiet --break-system-packages \
    anthropic requests pyserial \
    >> "$LOGFILE" 2>&1 \
    && log "pip packages OK" \
    || soft_fail "some pip packages failed"

# verify PyQt5
python3 -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')" \
    >> "$LOGFILE" 2>&1 \
    && log "PyQt5 verified" \
    || soft_fail "PyQt5 verify failed — GUI will fall back to CLI"
sep

# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 3 — VNC SERVER
# ══════════════════════════════════════════════════════════════════════════════
section "PHASE 3 — VNC SERVER"

VNC_TYPE=""
apt_install "TigerVNC" tigervnc-standalone-server tigervnc-common
command -v vncserver > /dev/null 2>&1 && VNC_TYPE="tiger"

if [ -z "$VNC_TYPE" ]; then
    warn "TigerVNC failed — trying TightVNC..."
    apt_install "TightVNC" tightvncserver
    command -v vncserver > /dev/null 2>&1 && VNC_TYPE="tight"
fi

[ -n "$VNC_TYPE" ] \
    && log "VNC server ready: $VNC_TYPE" \
    || fail "no VNC server installed!!"

apt_install "display utils" \
    dbus-x11 xauth x11-utils x11-xserver-utils xrandr
sep

# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 4 — XFCE4 DESKTOP
# ══════════════════════════════════════════════════════════════════════════════
section "PHASE 4 — XFCE4 DESKTOP"

apt_install "XFCE4" \
    xfce4 xfce4-terminal xfwm4 xfdesktop4 \
    xfce4-taskmanager xfce4-screenshooter \
    xfce4-whiskermenu-plugin \
    xfce4-notifyd xfce4-power-manager \
    thunar mousepad

apt_install "fonts" \
    fonts-hack fonts-noto fonts-firacode fonts-dejavu
sep

# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 5 — DARK THEME
# ══════════════════════════════════════════════════════════════════════════════
section "PHASE 5 — DARK THEME"

apt_install "themes + icons" \
    arc-theme papirus-icon-theme \
    gtk2-engines-murrine gtk2-engines-pixbuf

mkdir -p ~/.config/gtk-3.0 /etc/gtk-3.0

cat > ~/.config/gtk-3.0/settings.ini << 'GTK3'
[Settings]
gtk-theme-name=Arc-Dark
gtk-icon-theme-name=Papirus-Dark
gtk-font-name=Hack 10
gtk-application-prefer-dark-theme=1
GTK3

cat > ~/.gtkrc-2.0 << 'GTK2'
gtk-theme-name="Arc-Dark"
gtk-icon-theme-name="Papirus-Dark"
gtk-font-name="Hack 10"
GTK2

log "Arc-Dark theme configured"
sep

# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 6 — VNC CONFIG (Samsung S25 optimized)
# ══════════════════════════════════════════════════════════════════════════════
section "PHASE 6 — VNC CONFIG · S25 1080x1920"

mkdir -p ~/.vnc

# set VNC password
info "setting VNC password to: groot44"
printf "groot44\ngroot44\nn\n" | vncpasswd >> "$LOGFILE" 2>&1 \
    && log "VNC password set" \
    || soft_fail "vncpasswd failed — set manually with: vncpasswd"

# xstartup — S25 optimized
cat > ~/.vnc/xstartup << 'XSTARTUP'
#!/bin/bash
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
export DISPLAY=:1

# S25 resolution
xrandr --fb 1080x1920 2>/dev/null || true

# disable compositor — saves RAM
xfconf-query -c xfwm4 -p /general/use_compositing -s false 2>/dev/null || true

# disable blanking
xset s off 2>/dev/null || true
xset -dpms 2>/dev/null || true
xset s noblank 2>/dev/null || true

export $(dbus-launch)
exec startxfce4
XSTARTUP
chmod +x ~/.vnc/xstartup
log "xstartup configured for S25"

# XFCE4 — disable compositor for performance
mkdir -p ~/.config/xfce4/xfconf/xfce-perchannel-xml
cat > ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml << 'XFWM'
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfwm4" version="1.0">
  <property name="general" type="empty">
    <property name="use_compositing" type="bool" value="false"/>
    <property name="theme" type="string" value="Arc-Dark"/>
  </property>
</channel>
XFWM
log "XFCE4 compositor disabled"
sep

# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 7 — SOULWORN SCRIPT
# ══════════════════════════════════════════════════════════════════════════════
section "PHASE 7 — SOULWORN"

SOULWORN_DEST="$HOME/soulworn.py"

if [ -f "/sdcard/soulworn.py" ]; then
    cp /sdcard/soulworn.py "$SOULWORN_DEST"
    log "soulworn.py copied from sdcard"
elif [ -f "/storage/emulated/0/soulworn.py" ]; then
    cp /storage/emulated/0/soulworn.py "$SOULWORN_DEST"
    log "soulworn.py copied from storage"
else
    warn "soulworn.py not found on sdcard — download it to /sdcard/ first"
    warn "then run: cp /sdcard/soulworn.py ~/soulworn.py"
fi

chmod +x "$SOULWORN_DEST" 2>/dev/null || true
sep

# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 8 — SHELL + ALIASES
# ══════════════════════════════════════════════════════════════════════════════
section "PHASE 8 — SHELL SETUP"

# remove old nkit aliases if present
sed -i '/# ── SoulWoRn/,/^$/d' ~/.bashrc 2>/dev/null || true

cat >> ~/.bashrc << 'BASHRC'

# ── SoulWoRn aliases ─────────────────────────────────────────────────────────
export DISPLAY=:1
export TERM=xterm-256color

# VNC control
alias vnc-start='vncserver -kill :1 2>/dev/null; vncserver :1 -geometry 1080x1920 -depth 24 -dpi 393'
alias vnc-stop='vncserver -kill :1'
alias vnc-restart='vncserver -kill :1 2>/dev/null; sleep 1; vncserver :1 -geometry 1080x1920 -depth 24 -dpi 393'
alias vnc-status='pgrep -a vnc'

# SoulWoRn
alias sw='python3 ~/soulworn.py --cli'
alias sw-gui='DISPLAY=:1 python3 ~/soulworn.py'
alias soulworn='python3 ~/soulworn.py --cli'

# general
alias ll='ls -lah --color=auto'
alias la='ls -la --color=auto'
alias cls='clear'
alias py='python3'
alias update='apt-get update && apt-get upgrade -y'

# prompt
PS1='\[\033[91m\][SoulWoRn]\[\033[0m\] \[\033[96m\]\w\[\033[0m\] 👽 $ '
BASHRC

log "shell aliases configured"
sep

# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 9 — QUICK LAUNCH SCRIPTS
# ══════════════════════════════════════════════════════════════════════════════
section "PHASE 9 — LAUNCH SCRIPTS"

# vnc start script
cat > ~/start-vnc.sh << 'VNC'
#!/bin/bash
echo "  stopping any existing VNC..."
vncserver -kill :1 2>/dev/null || true
sleep 1
echo "  starting VNC for Samsung S25..."
vncserver :1 \
    -geometry 1080x1920 \
    -depth 24 \
    -dpi 393 \
    -localhost no
echo ""
echo "  ✓ VNC running on port 5901"
echo "  connect bVNC:"
echo "    Type:     Plain VNC"
echo "    Server:   localhost"
echo "    Port:     5901"
echo "    Password: groot44"
echo ""
VNC
chmod +x ~/start-vnc.sh
log "start-vnc.sh created"

# soulworn launch script
cat > ~/start-soulworn.sh << 'SW'
#!/bin/bash
echo "  launching SoulWoRn..."
if [ -n "$DISPLAY" ]; then
    python3 ~/soulworn.py
else
    python3 ~/soulworn.py --cli
fi
SW
chmod +x ~/start-soulworn.sh
log "start-soulworn.sh created"

# combined launcher
cat > ~/go.sh << 'GO'
#!/bin/bash
# SoulWoRn full launcher
# starts VNC + opens SoulWoRn

RED='\033[91m'
CYAN='\033[96m'
GREEN='\033[92m'
RESET='\033[0m'

echo -e "${CYAN}  SoulWoRn launcher 👽${RESET}"
echo ""
echo -e "  ${GREEN}1${RESET}) start VNC + SoulWoRn GUI"
echo -e "  ${GREEN}2${RESET}) SoulWoRn CLI only"
echo -e "  ${GREEN}3${RESET}) just start VNC"
echo -e "  ${GREEN}4${RESET}) stop VNC"
echo ""
read -p "  select > " choice

case $choice in
    1)
        vncserver -kill :1 2>/dev/null || true
        sleep 1
        vncserver :1 -geometry 1080x1920 -depth 24 -dpi 393
        export DISPLAY=:1
        sleep 2
        python3 ~/soulworn.py
        ;;
    2)
        python3 ~/soulworn.py --cli
        ;;
    3)
        vncserver -kill :1 2>/dev/null || true
        sleep 1
        vncserver :1 -geometry 1080x1920 -depth 24 -dpi 393
        echo -e "  ${GREEN}VNC running — connect bVNC to localhost:5901${RESET}"
        ;;
    4)
        vncserver -kill :1
        echo -e "  ${GREEN}VNC stopped${RESET}"
        ;;
    *)
        python3 ~/soulworn.py --cli
        ;;
esac
GO
chmod +x ~/go.sh
log "go.sh launcher created"
sep

# ══════════════════════════════════════════════════════════════════════════════
#  CLEANUP
# ══════════════════════════════════════════════════════════════════════════════
section "CLEANUP"
apt-get autoremove -y -qq >> "$LOGFILE" 2>&1 || true
apt-get autoclean -y -qq >> "$LOGFILE" 2>&1 || true
log "cleanup done"
sep

# ══════════════════════════════════════════════════════════════════════════════
#  SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}║          SOULWORN SETUP COMPLETE  👽                 ║${RESET}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "  ${GREEN}VNC:${RESET}      1080x1920 · 393dpi · port 5901"
echo -e "  ${GREEN}password:${RESET} groot44"
echo -e "  ${GREEN}theme:${RESET}    Arc-Dark + Papirus"
echo -e "  ${GREEN}PyQt5:${RESET}    installed"
echo ""
echo -e "  ${CYAN}QUICK COMMANDS:${RESET}"
echo -e "  ${WHITE}  bash ~/go.sh${RESET}           ← launcher menu"
echo -e "  ${WHITE}  bash ~/start-vnc.sh${RESET}    ← start VNC"
echo -e "  ${WHITE}  sw${RESET}                     ← SoulWoRn CLI"
echo -e "  ${WHITE}  sw-gui${RESET}                 ← SoulWoRn GUI (needs VNC)"
echo ""
echo -e "  ${CYAN}bVNC SETTINGS:${RESET}"
echo -e "  ${WHITE}  Type:     Plain VNC${RESET}"
echo -e "  ${WHITE}  Server:   localhost${RESET}"
echo -e "  ${WHITE}  Port:     5901${RESET}"
echo -e "  ${WHITE}  Password: groot44${RESET}"
echo ""

if [ ${#ERRORS[@]} -gt 0 ]; then
    echo -e "  ${YELLOW}non-fatal warnings:${RESET}"
    for e in "${ERRORS[@]}"; do
        echo -e "  ${DIM}  · $e${RESET}"
    done
    echo ""
fi

echo -e "  ${DIM}log: $LOGFILE${RESET}"
echo -e "  ${DIM}👽 nofatchicks · kelowna bc · GPL-3.0${RESET}"
echo ""
echo -e "  ${CYAN}run: source ~/.bashrc then: bash ~/go.sh${RESET}"
echo ""
