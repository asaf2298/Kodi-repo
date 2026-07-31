# userdata/autoexec.py
# Personal Build — One-Shot Boot Automation
# Copy this file to: Kodi/userdata/autoexec.py
# Runs automatically every time Kodi starts.

import xbmc
import xbmcaddon
import xbmcgui


def check_trakt_auth():
    """Trigger Trakt authorization if token is missing."""
    try:
        trakt = xbmcaddon.Addon("script.trakt")
        token = trakt.getSetting("authorization.token")
        if not token or token.strip() == "":
            xbmc.sleep(4000)  # Wait for Kodi UI to fully load
            xbmcgui.Dialog().notification(
                "Personal Build",
                "מחבר Trakt — אנא המתן...",
                xbmcgui.NOTIFICATION_INFO,
                4000
            )
            xbmc.sleep(1000)
            xbmc.executebuiltin("RunScript(script.trakt,authorize)")
        else:
            xbmc.log("[Personal Build] Trakt already authorized, skipping.", xbmc.LOGINFO)
    except Exception as e:
        # Trakt not installed yet — silent skip
        xbmc.log(f"[Personal Build] autoexec: Trakt check skipped: {e}", xbmc.LOGWARNING)


# Give Kodi 2 seconds to fully initialize
xbmc.sleep(2000)
check_trakt_auth()
