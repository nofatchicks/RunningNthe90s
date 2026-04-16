#!/bin/bash
# ╔══════════════════════════════════════════════════════════════════╗
# ║   SoulWoRn — GitHub Setup Script · Arch Linux Edition           ║
# ║   nofatchicks · GPL-3.0 · 👽                                    ║
# ╚══════════════════════════════════════════════════════════════════╝

RED='\033[38;5;160m'
ROYAL='\033[38;5;93m'
VIOLET='\033[38;5;135m'
GOLD='\033[38;5;220m'
GREEN='\033[38;5;46m'
GREY='\033[38;5;245m'
WHITE='\033[97m'
DIM='\033[2m'
RESET='\033[0m'

log()     { echo -e "${GREEN}  ✓${RESET}  $1"; }
info()    { echo -e "${ROYAL}  ──${RESET}  $1"; }
warn()    { echo -e "${GOLD}  ⚠${RESET}   $1"; }
fail()    { echo -e "${RED}  ✗${RESET}  $1"; }
sep()     { echo -e "${DIM}  ────────────────────────────────────────${RESET}"; }
section() { echo -e "\n${ROYAL}  [$1]${RESET}\n"; }

clear
echo -e "${RED}"
cat << 'BANNER'
  ██████╗ ██╗████████╗██╗  ██╗██╗   ██╗██████╗
  ██╔════╝██║╚══██╔══╝██║  ██║██║   ██║██╔══██╗
  ██║  ███╗██║   ██║   ███████║██║   ██║██████╔╝
  ██║   ██║██║   ██║   ██╔══██║██║   ██║██╔══██╗
  ╚██████╔╝██║   ██║   ██║  ██║╚██████╔╝██████╔╝
   ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═════╝
  SoulWoRn · GitHub Setup · Arch Linux · nofatchicks 👽
BANNER
echo -e "${RESET}"

# ── STEP 1 — install git ──────────────────────────────────────────────────────
section "STEP 1 — INSTALL GIT"
if command -v git > /dev/null 2>&1; then
    log "git already installed: $(git --version)"
else
    info "installing git..."
    sudo pacman -S --needed --noconfirm git curl openssh \
        && log "git installed" \
        || { fail "pacman failed!!"; exit 1; }
fi
sep

# ── STEP 2 — identity ─────────────────────────────────────────────────────────
section "STEP 2 — GIT IDENTITY"

CURRENT_NAME=$(git config --global user.name 2>/dev/null)
CURRENT_EMAIL=$(git config --global user.email 2>/dev/null)

if [ -n "$CURRENT_NAME" ]; then
    info "current name:  $CURRENT_NAME"
    info "current email: $CURRENT_EMAIL"
    read -p "  keep these? [Y/n] > " keep
    if [[ "$keep" =~ ^[Nn]$ ]]; then
        read -p "  GitHub username > " GH_USER
        read -p "  email > " GH_EMAIL
        git config --global user.name "$GH_USER"
        git config --global user.email "$GH_EMAIL"
    fi
else
    read -p "  GitHub username (e.g. nofatchicks) > " GH_USER
    read -p "  email > " GH_EMAIL
    git config --global user.name "$GH_USER"
    git config --global user.email "$GH_EMAIL"
fi

log "identity set: $(git config --global user.name) <$(git config --global user.email)>"
sep

# ── STEP 3 — credential storage ───────────────────────────────────────────────
section "STEP 3 — CREDENTIAL STORAGE"

git config --global credential.helper store
git config --global core.editor "nano"
git config --global init.defaultBranch main
git config --global pull.rebase false
log "credential helper: store (~/.git-credentials)"
log "default branch: main"
log "default editor: nano"
sep

# ── STEP 4 — SSH key (optional but recommended) ───────────────────────────────
section "STEP 4 — SSH KEY (optional)"
info "SSH keys = no token needed ever again"
info "HTTPS tokens = easier setup but must store manually"
echo ""
echo -e "  ${RED}[1]${RESET}  generate SSH key  ${DIM}(recommended)${RESET}"
echo -e "  ${RED}[2]${RESET}  use HTTPS + token  ${DIM}(simpler)${RESET}"
echo ""
read -p "  select > " auth_choice

if [ "$auth_choice" = "1" ]; then
    SSH_KEY="$HOME/.ssh/id_ed25519_github"
    if [ -f "$SSH_KEY" ]; then
        warn "SSH key already exists at $SSH_KEY"
    else
        info "generating ed25519 SSH key..."
        ssh-keygen -t ed25519 -C "$(git config --global user.email)" \
            -f "$SSH_KEY" -N ""
        log "SSH key generated: $SSH_KEY"
    fi

    echo ""
    echo -e "${GOLD}  ══════════════════════════════════════════════${RESET}"
    echo -e "${GOLD}  ADD THIS PUBLIC KEY TO GITHUB:${RESET}"
    echo -e "${GOLD}  github.com → Settings → SSH Keys → New SSH Key${RESET}"
    echo -e "${GOLD}  ══════════════════════════════════════════════${RESET}"
    echo ""
    cat "$SSH_KEY.pub"
    echo ""
    echo -e "${GOLD}  ══════════════════════════════════════════════${RESET}"
    echo ""

    # add to ssh config
    mkdir -p ~/.ssh
    cat >> ~/.ssh/config << SSHCONF

Host github.com
    HostName github.com
    User git
    IdentityFile $SSH_KEY
    AddKeysToAgent yes
SSHCONF
    chmod 600 ~/.ssh/config
    log "SSH config written"

    # start ssh-agent
    eval "$(ssh-agent -s)" > /dev/null
    ssh-add "$SSH_KEY" 2>/dev/null
    log "key added to ssh-agent"

    read -p "  press enter AFTER adding key to github.com ..."
    ssh -T git@github.com 2>&1 | grep -q "success" \
        && log "SSH connection to GitHub: OK!!" \
        || warn "test: ssh -T git@github.com (may show warning — that's fine)"

    GH_PROTO="ssh"

else
    echo ""
    echo -e "${GOLD}  GET A TOKEN:${RESET}"
    echo -e "  github.com → Settings → Developer Settings"
    echo -e "  → Personal Access Tokens → Tokens (classic)"
    echo -e "  → Generate new token → check: repo + workflow"
    echo -e "  token starts with: ${WHITE}ghp_...${RESET}"
    echo ""
    read -p "  paste token now (hidden) > " -s GH_TOKEN
    echo ""

    if [ -n "$GH_TOKEN" ]; then
        GH_USER_STORED=$(git config --global user.name)
        echo "https://${GH_USER_STORED}:${GH_TOKEN}@github.com" > ~/.git-credentials
        chmod 600 ~/.git-credentials
        log "token stored in ~/.git-credentials"
    else
        warn "no token entered — you'll be prompted on first push"
    fi
    GH_PROTO="https"
fi
sep

# ── STEP 5 — clone or init SoulWoRn repo ─────────────────────────────────────
section "STEP 5 — SOULWORN REPO"

GH_USER_NAME=$(git config --global user.name)
REPO_NAME="soulworn"

echo -e "  ${RED}[1]${RESET}  clone existing repo  ${DIM}(github.com/${GH_USER_NAME}/${REPO_NAME})${RESET}"
echo -e "  ${RED}[2]${RESET}  init new local repo + push"
echo -e "  ${RED}[0]${RESET}  skip"
echo ""
read -p "  select > " repo_choice

if [ "$repo_choice" = "1" ]; then
    cd ~
    if [ "$GH_PROTO" = "ssh" ]; then
        URL="git@github.com:${GH_USER_NAME}/${REPO_NAME}.git"
    else
        URL="https://github.com/${GH_USER_NAME}/${REPO_NAME}.git"
    fi
    info "cloning $URL..."
    git clone "$URL" \
        && log "cloned to ~/${REPO_NAME}" \
        || fail "clone failed — check repo exists + credentials"

elif [ "$repo_choice" = "2" ]; then
    mkdir -p ~/$REPO_NAME
    cd ~/$REPO_NAME
    git init
    log "git init done in ~/$REPO_NAME"

    # copy soulworn_arch.py if it exists
    for src in \
        ~/downloads/soulworn_arch.py \
        /sdcard/soulworn_arch.py \
        ~/soulworn_arch.py; do
        if [ -f "$src" ]; then
            cp "$src" .
            log "copied soulworn_arch.py from $src"
            break
        fi
    done

    cat > README.md << README
# SoulWoRn 👽
Android toolbox for Arch Linux + Termux.
No PC needed. GPL-3.0.
Samsung S8+ · Pixels · MTK · Any Android 2012+
NO telemetry · Blood Red + Royal Purple
github.com/${GH_USER_NAME}/${REPO_NAME}
README

    git add .
    git commit -m "SoulWoRn init — ghost in the machine 👽"
    git branch -M main

    if [ "$GH_PROTO" = "ssh" ]; then
        REMOTE="git@github.com:${GH_USER_NAME}/${REPO_NAME}.git"
    else
        REMOTE="https://github.com/${GH_USER_NAME}/${REPO_NAME}.git"
    fi

    git remote add origin "$REMOTE"
    info "pushing to $REMOTE..."
    git push -u origin main \
        && log "pushed!!" \
        || fail "push failed — make sure repo exists on github.com first"
fi
sep

# ── STEP 6 — aliases ──────────────────────────────────────────────────────────
section "STEP 6 — GIT ALIASES"

# remove old aliases if present
sed -i '/# ── SoulWoRn git/,/^$/d' ~/.bashrc 2>/dev/null || true

cat >> ~/.bashrc << 'ALIASES'

# ── SoulWoRn git aliases ─────────────────────────────────────────────────────
alias push='git add . && git commit -m "update 👽 $(date +%Y-%m-%d)" && git push'
alias gpush='f(){ git add . && git commit -m "$1" && git push; }; f'
alias gst='git status'
alias glog='git log --oneline --graph --all'
alias gdiff='git diff'
alias gnew='f(){ git checkout -b "$1"; }; f'
alias gsync='git pull origin main'
ALIASES

log "aliases added to ~/.bashrc"
info "push          — quick add+commit+push with date"
info "gpush 'msg'   — push with custom message"
info "gst           — git status"
info "glog          — pretty log"
info "gsync         — pull latest"
sep

# ── DONE ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "${RED}╔══════════════════════════════════════════════════════╗${RESET}"
echo -e "${RED}║        GITHUB SETUP COMPLETE  👽                     ║${RESET}"
echo -e "${RED}╚══════════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "  ${ROYAL}daily workflow:${RESET}"
echo -e "  ${WHITE}  cd ~/soulworn${RESET}"
echo -e "  ${WHITE}  # edit files...${RESET}"
echo -e "  ${WHITE}  push${RESET}              ${DIM}← one command does everything${RESET}"
echo -e "  ${WHITE}  gpush 'my message'${RESET}  ${DIM}← custom commit message${RESET}"
echo ""
echo -e "  ${ROYAL}manual workflow:${RESET}"
echo -e "  ${WHITE}  git add .${RESET}"
echo -e "  ${WHITE}  git commit -m 'message'${RESET}"
echo -e "  ${WHITE}  git push origin main${RESET}"
echo ""
echo -e "  ${DIM}source ~/.bashrc to load aliases${RESET}"
echo -e "  ${DIM}👽 nofatchicks · kelowna bc · GPL-3.0${RESET}"
echo ""
