# userdata/autoexec.py — Personal Build v1.5.0
# Runs automatically on every Kodi boot.
# Handles: addon install verification + Trakt one-shot authorization.

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import json


REQUIRED_ADDONS = [
    "plugin.video.personal",
    "script.trakt",
    "script.module.requests",
]


def check_missing_addons():
    """Warn if any required addon is not installed."""
    missing = []
    for addon_id in REQUIRED_ADDONS:
        try:
            xbmcaddon.Addon(addon_id)
        except Exception:
            missing.append(addon_id)
    if missing:
        xbmcgui.Dialog().notification(
            "Personal Build",
            f"חסרים {len(missing)} תוספים: " + ", ".join(missing),
            xbmcgui.NOTIFICATION_WARNING,
            6000
        )
        xbmc.log(f"[Personal Build] Missing addons: {missing}", xbmc.LOGWARNING)
    return missing


def check_trakt_auth():
    """Trigger Trakt authorization only if token is missing."""
    try:
        trakt = xbmcaddon.Addon("script.trakt")
        token = trakt.getSetting("authorization.token")
        if not token or token.strip() == "":
            xbmc.sleep(4000)
            xbmcgui.Dialog().notification(
                "Personal Build",
                "מחבר Trakt — אנא המתן...",
                xbmcgui.NOTIFICATION_INFO,
                4000
            )
            xbmc.sleep(1000)
            xbmc.executebuiltin("RunScript(script.trakt,authorize)")
        else:
            xbmc.log("[Personal Build] Trakt already authorized.", xbmc.LOGINFO)
    except Exception as e:
        xbmc.log(f"[Personal Build] Trakt check skipped: {e}", xbmc.LOGWARNING)


# Wait for Kodi UI to settle
xbmc.sleep(2000)
check_missing_addons()
check_trakt_auth()
