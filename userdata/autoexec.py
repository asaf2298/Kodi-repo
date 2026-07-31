# userdata/autoexec.py — runs once on every Kodi boot
import xbmc
import xbmcaddon
import xbmcgui

def check_trakt():
    try:
        trakt = xbmcaddon.Addon("script.trakt")
        token = trakt.getSetting("authorization.token")
        if not token:
            xbmc.sleep(3000)  # Wait for UI to settle
            xbmcgui.Dialog().notification(
                "Personal Build", "מאשר Trakt — אנא המתן...",
                xbmcgui.NOTIFICATION_INFO, 4000
            )
            xbmc.executebuiltin("RunScript(script.trakt,authorize)")
    except Exception:
        pass  # Trakt not installed yet, skip silently

xbmc.sleep(2000)
check_trakt()