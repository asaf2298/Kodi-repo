#!/usr/bin/env python3
"""
Personal Kodi Build - Automated Installer
==========================================
Run this script ONCE on any machine with Kodi installed.
It auto-detects your Kodi userdata folder and copies all
required files for the Personal build to the correct locations.

Usage:
  python install.py           # interactive prompt
  python install.py light     # install Light build directly
  python install.py heavy     # install Heavy build directly

Works on: Windows, Linux, macOS, Android (via Termux)
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path

# ── Colours ────────────────────────────────────────────────────────────────
if platform.system() == "Windows":
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleMode(
            ctypes.windll.kernel32.GetStdHandle(-11), 7
        )
    except Exception:
        pass

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):   print(f"{GREEN}  ✓  {msg}{RESET}")
def warn(msg): print(f"{YELLOW}  ⚠  {msg}{RESET}")
def err(msg):  print(f"{RED}  ✗  {msg}{RESET}")
def info(msg): print(f"{CYAN}  →  {msg}{RESET}")
def head(msg): print(f"\n{BOLD}{msg}{RESET}")

# ── Kodi path detection ─────────────────────────────────────────────────────
def find_kodi_userdata() -> Path | None:
    system = platform.system()
    candidates = []

    if system == "Windows":
        appdata = os.environ.get("APPDATA", "")
        candidates = [
            Path(appdata) / "Kodi",
            Path("C:/Kodi"),
            Path(os.environ.get("LOCALAPPDATA", "")) / "Kodi",
        ]
    elif system == "Darwin":  # macOS
        home = Path.home()
        candidates = [
            home / "Library" / "Application Support" / "Kodi",
        ]
    elif system == "Linux":
        home = Path.home()
        candidates = [
            home / ".kodi",
            Path("/storage/.kodi"),           # LibreELEC / CoreELEC
            Path("/data/data/org.xbmc.kodi/files/.kodi"),  # Android
        ]
    else:
        # Android / Termux fallback
        candidates = [
            Path("/sdcard/Android/data/org.xbmc.kodi/files/.kodi"),
            Path("/data/data/org.xbmc.kodi/files/.kodi"),
        ]

    for path in candidates:
        userdata = path / "userdata"
        if userdata.exists():
            return userdata

    return None


def check_kodi_running() -> bool:
    """Returns True if Kodi process is running."""
    system = platform.system()
    try:
        if system == "Windows":
            out = subprocess.check_output("tasklist", shell=True).decode()
            return "kodi" in out.lower()
        else:
            out = subprocess.check_output(["pgrep", "-x", "kodi"], stderr=subprocess.DEVNULL)
            return True
    except Exception:
        return False


# ── File copy helpers ────────────────────────────────────────────────────────
def copy_file(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    ok(f"{dst.relative_to(dst.anchor)}")


def copy_dir(src: Path, dst: Path):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    ok(f"{dst.name}/ → copied")


# ── Main installer ───────────────────────────────────────────────────────────
def main():
    head("Personal Kodi Build — Installer v1.5.0")
    print("  https://github.com/asaf2298/Kodi-repo\n")

    # Determine script location (repo root)
    repo_root = Path(__file__).parent.resolve()

    # ── Build profile selection ──────────────────────────────────────────────
    profile = None
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("light", "heavy"):
        profile = sys.argv[1].lower()
    else:
        print("  Which build do you want to install?")
        print("  [1] Light System  — Android TV, FireStick (recommended)")
        print("  [2] Heavy System  — PC, Nvidia Shield (full catalog)")
        choice = input("  Enter 1 or 2: ").strip()
        profile = "light" if choice == "1" else "heavy"

    info(f"Selected profile: {profile.upper()}")

    # ── Kodi userdata detection ──────────────────────────────────────────────
    head("Detecting Kodi userdata folder...")
    kodi_userdata = find_kodi_userdata()

    if not kodi_userdata:
        err("Could not find Kodi userdata folder automatically.")
        manual = input("  Enter full path to your Kodi userdata folder: ").strip()
        kodi_userdata = Path(manual)
        if not kodi_userdata.exists():
            err(f"Path does not exist: {kodi_userdata}")
            sys.exit(1)

    ok(f"Found: {kodi_userdata}")
    kodi_root   = kodi_userdata.parent          # e.g. %APPDATA%/Kodi
    kodi_addons = kodi_root / "addons"

    # ── Check Kodi is not running ────────────────────────────────────────────
    head("Checking if Kodi is running...")
    if check_kodi_running():
        warn("Kodi is currently running. Please close it before installing.")
        input("  Press Enter once Kodi is closed to continue...")

    ok("Kodi is not running.")

    # ── Source paths ─────────────────────────────────────────────────────────
    shared_userdata = repo_root / "build-shared" / "userdata"
    profile_data    = repo_root / f"build-{profile}" / "userdata"
    addon_src       = repo_root / "plugin.video.personal"

    # ── 1. Copy autoexec.py ──────────────────────────────────────────────────
    head("[1/5] Installing autoexec.py...")
    copy_file(
        shared_userdata / "autoexec.py",
        kodi_userdata / "autoexec.py"
    )

    # ── 2. Copy shortcuts (mainmenu.DATA.xml) ────────────────────────────────
    head("[2/5] Installing home menu shortcuts...")
    shortcuts_dst = kodi_userdata / "shortcuts"
    shortcuts_dst.mkdir(parents=True, exist_ok=True)
    copy_file(
        shared_userdata / "shortcuts" / "mainmenu.DATA.xml",
        shortcuts_dst / "mainmenu.DATA.xml"
    )

    # ── 3. Copy plugin.video.personal addon ─────────────────────────────────
    head("[3/5] Installing plugin.video.personal...")
    if addon_src.exists():
        copy_dir(addon_src, kodi_addons / "plugin.video.personal")
    else:
        warn("plugin.video.personal folder not found in repo — skipping.")

    # ── 4. Copy addon_data settings ─────────────────────────────────────────
    head("[4/5] Installing addon settings...")
    addon_data_src = profile_data / "addon_data"
    addon_data_dst = kodi_userdata / "addon_data"

    if addon_data_src.exists():
        for addon_folder in addon_data_src.iterdir():
            if addon_folder.is_dir():
                dst_addon = addon_data_dst / addon_folder.name
                dst_addon.mkdir(parents=True, exist_ok=True)
                for f in addon_folder.iterdir():
                    copy_file(f, dst_addon / f.name)
    else:
        warn(f"No addon_data found for profile: {profile}")

    # ── 5. Summary ───────────────────────────────────────────────────────────
    head("[5/5] Installation complete!")
    print(f"""
{GREEN}{BOLD}  ✅ Personal Build ({profile.upper()}) installed successfully!{RESET}

  Next steps:
  {CYAN}1.{RESET} Open Kodi
  {CYAN}2.{RESET} Trakt authorization will trigger automatically on first boot
  {CYAN}3.{RESET} Home menu shortcuts are pre-configured (no skin setup needed)

  Kodi userdata: {kodi_userdata}
""")

    if platform.system() == "Windows":
        input("  Press Enter to exit...")


if __name__ == "__main__":
    main()
