# main.py — Personal Kodi Add-on v1.5.0
# Movies / Series / Anime / Live TV + Dual System Tokens + Subtitles + Dynamic Skin Switching

import sys
import json
import urllib.parse
import requests
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

ADDON = xbmcaddon.Addon()
ADDON_HANDLE = int(sys.argv[1])
BASE_URL = "https://user-manager-lime.vercel.app"

# ==============================================================================
# Dual System Tokens & Target Skins
# ==============================================================================
TOKEN_LIGHT = "123kodi123token123friend_light"
TOKEN_HEAVY = "123kodi123token123everything"
TARGET_LIGHT_SKIN = "skin.arctic.zephyr.mod"   # matches guisettings.xml
TARGET_HEAVY_SKIN = "skin.arctic.horizon.2"


def get_active_token():
    """
    Returns token based on add-on setting.
    Optional override via settings user_key_override field.
    """
    override = ADDON.getSetting("user_key_override").strip()
    if override:
        return override
    profile_choice = ADDON.getSetting("system_profile")
    return TOKEN_HEAVY if profile_choice == "1" else TOKEN_LIGHT


def get_current_skin():
    """Read the active skin addon ID via JSON-RPC (correct method)."""
    result = xbmc.executeJSONRPC(
        '{"jsonrpc":"2.0","method":"Settings.GetSettingValue","id":1,'
        '"params":{"setting":"lookandfeel.skin"}}'
    )
    try:
        return json.loads(result).get("result", {}).get("value", "")
    except Exception:
        return ""


def apply_skin_profile():
    """
    Switches skin only when on the home screen (no action param).
    Avoids repeated JSON-RPC calls on every catalog navigation.
    """
    profile_choice = ADDON.getSetting("system_profile")
    current_skin = get_current_skin()
    target = TARGET_HEAVY_SKIN if profile_choice == "1" else TARGET_LIGHT_SKIN
    if current_skin != target:
        xbmc.executeJSONRPC(
            '{"jsonrpc":"2.0","method":"Settings.SetSettingValue","id":1,'
            f'"params":{{"setting":"lookandfeel.skin","value":"{target}"}}}}'
        )
        label = "Heavy" if profile_choice == "1" else "Light"
        xbmcgui.Dialog().notification(
            "Personal Build",
            f"Switched to {label} Skin Profile",
            xbmcgui.NOTIFICATION_INFO,
            3000
        )


def build_url(query):
    return sys.argv[0] + "?" + urllib.parse.urlencode(query)


def build_external_url(addon_id, route, **params):
    """
    Build a plugin:// URL for a route in another installed addon (SlyGuy's
    Pluto/Roku providers), matching script.module.slyguy's own router.build_url()
    encoding exactly: the route name goes in the '_' param, then every param is
    urlencoded together sorted by key. Confirmed against the real addon source
    (script.module.slyguy/resources/modules/slyguy/router.py) and against how
    each addon's own home menu links to itself (e.g. plugin.url_for(live_tv)).
    """
    all_params = {"_": route}
    all_params.update(params)
    query = urllib.parse.urlencode(sorted(all_params.items()))
    return f"plugin://{addon_id}/?{query}"


def get_params():
    return dict(urllib.parse.parse_qsl(sys.argv[2][1:]))


def show_error(msg):
    xbmcgui.Dialog().notification("Personal", msg, xbmcgui.NOTIFICATION_ERROR)


def api_get(url, timeout=10):
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


# ==============================================================================
# Directory Builders
# ==============================================================================

def list_root():
    xbmcplugin.setContent(ADDON_HANDLE, "files")
    categories = [
        ("סרטים", "movie"),
        ("סדרות", "series"),
        ("אנימה", "anime"),
        ("שידור חי", "tv"),
    ]
    for label, content_type in categories:
        li = xbmcgui.ListItem(label=label)
        li.setIsFolder(True)
        xbmcplugin.addDirectoryItem(
            ADDON_HANDLE,
            build_url({"action": "type_root", "type": content_type}),
            li, True
        )
    xbmcplugin.endOfDirectory(ADDON_HANDLE)


PLUTO_NEWS_GROUP = "News + Opinion"  # matches i.mjh.nz/PlutoTV's real "us" channel group tag


def list_live_tv_root():
    """
    Live TV landing: 3 rows -- Kan-Box (Israeli, via our own backend), Pluto TV
    US News (deep link into the real bundled addon's own channel-group folder,
    no reimplementation), and Roku (its own Live TV + Search, one level down).
    """
    xbmcplugin.setContent(ADDON_HANDLE, "files")

    li = xbmcgui.ListItem(label="ערוצים חיים - ישראל (Kan-Box)")
    li.setIsFolder(True)
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, build_url({"action": "live_tv_kanbox"}), li, True)

    li = xbmcgui.ListItem(label="חדשות ארה\"ב - Pluto TV")
    li.setIsFolder(True)
    xbmcplugin.addDirectoryItem(
        ADDON_HANDLE,
        build_external_url("slyguy.pluto.tv.provider", "live_tv", code="us", group=PLUTO_NEWS_GROUP),
        li, True
    )

    li = xbmcgui.ListItem(label="Roku")
    li.setIsFolder(True)
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, build_url({"action": "roku_root"}), li, True)

    xbmcplugin.endOfDirectory(ADDON_HANDLE)


def list_roku_root():
    """Roku row's own sub-menu: its native Live TV browse and Search, unfiltered."""
    xbmcplugin.setContent(ADDON_HANDLE, "files")

    li = xbmcgui.ListItem(label="Live TV")
    li.setIsFolder(True)
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, build_external_url("slyguy.roku", "live_tv"), li, True)

    li = xbmcgui.ListItem(label="Search")
    li.setIsFolder(True)
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, build_external_url("slyguy.roku", "search"), li, True)

    xbmcplugin.endOfDirectory(ADDON_HANDLE)


def list_live_tv_kanbox():
    xbmcplugin.setContent(ADDON_HANDLE, "videos")
    try:
        data = api_get(
            f"{BASE_URL}/api/kodi-catalog?userKey={get_active_token()}&list=live_channels"
        )
    except Exception as e:
        show_error("שגיאת חיבור: " + str(e))
        return
    for item in data.get("items", []):
        li = xbmcgui.ListItem(label=item["title"])
        li.setArt({"poster": item.get("poster", ""), "fanart": item.get("fanart", "")})
        li.setProperty("IsPlayable", "true")
        # Use direct URL if available (live TV bypasses stream resolver)
        stream_url = item.get("url") or build_url({
            "action": "streams",
            "type": "tv",
            "imdb_id": item.get("imdb_id", item["title"]),
            "title": item["title"],
        })
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, stream_url, li, False)
    xbmcplugin.endOfDirectory(ADDON_HANDLE)


def list_type_root(content_type):
    xbmcplugin.setContent(ADDON_HANDLE, "files")
    try:
        data = api_get(
            f"{BASE_URL}/api/kodi-catalog?userKey={get_active_token()}&list=catalogs"
        )
    except Exception as e:
        show_error("שגיאת חיבור: " + str(e))
        return
    matching = [c for c in data.get("catalogs", []) if c["type"] == content_type]
    if not matching:
        show_error("לא נמצאו קטלוגים לסוג הזה")
        return
    for cat in matching:
        li = xbmcgui.ListItem(label=cat["name"])
        li.setIsFolder(True)
        xbmcplugin.addDirectoryItem(
            ADDON_HANDLE,
            build_url({"action": "catalog", "type": cat["type"], "catalogId": cat["id"]}),
            li, True
        )
    xbmcplugin.endOfDirectory(ADDON_HANDLE)


# Pure-anime rows from AnimeIL (never Cinemeta -- its genre=Animation would mix
# in non-anime Western cartoons). AnimeIL only accepts one genre per request, so
# each row combines a few genres by fanning out and merging server-side
# (api/kodi-catalog.js's list=anime_genres). Order and grouping as specified.
ANIME_GENRE_ROWS = [
    ("מדע בדיוני והרפתקאות", ["Sci-Fi", "Fantasy", "Action", "War", "Adventure"]),
    ("מתח ואימה", ["Thriller", "Mystery", "Horror", "Crime", "Drama"]),
    ("רומנטיקה וקומדיה", ["Romance", "Family", "Comedy"]),
    ("מוזיקה וספורט", ["Music", "History", "Sport", "Short", "Animation"]),
]


def list_anime_root():
    xbmcplugin.setContent(ADDON_HANDLE, "files")
    for label, genre_list in ANIME_GENRE_ROWS:
        li = xbmcgui.ListItem(label=label)
        li.setIsFolder(True)
        xbmcplugin.addDirectoryItem(
            ADDON_HANDLE,
            build_url({"action": "anime_genre_combo", "genres": ",".join(genre_list)}),
            li, True
        )
    xbmcplugin.endOfDirectory(ADDON_HANDLE)


def list_anime_genre_combo(genres_csv):
    xbmcplugin.setContent(ADDON_HANDLE, "tvshows")
    try:
        data = api_get(
            f"{BASE_URL}/api/kodi-catalog?userKey={get_active_token()}"
            f"&list=anime_genres&genres={urllib.parse.quote(genres_csv)}"
        )
    except Exception as e:
        show_error("שגיאת חיבור: " + str(e))
        return
    for item in data.get("items", []):
        li = xbmcgui.ListItem(label=item["title"])
        li.setArt({"poster": item.get("poster", ""), "fanart": item.get("fanart", "")})
        li.setInfo("video", {
            "title": item["title"],
            "plot": item.get("plot", ""),
            "year": item.get("year", ""),
            "genre": item.get("genres", ""),
        })
        if item.get("imdb_id"):
            li.setUniqueIDs({"imdb": item["imdb_id"]}, "imdb")
        xbmcplugin.addDirectoryItem(
            ADDON_HANDLE,
            build_url({
                "action": "streams",
                "type": item["type"],
                "imdb_id": item["imdb_id"],
                "title": item["title"],
            }),
            li, True
        )
    xbmcplugin.endOfDirectory(ADDON_HANDLE)


def list_catalog_items(catalog_type, catalog_id):
    xbmcplugin.setContent(
        ADDON_HANDLE, "movies" if catalog_type == "movie" else "tvshows"
    )
    try:
        data = api_get(
            f"{BASE_URL}/api/kodi-catalog?userKey={get_active_token()}"
            f"&type={catalog_type}&catalogId={catalog_id}"
        )
    except Exception as e:
        show_error("שגיאת חיבור: " + str(e))
        return
    for item in data.get("items", []):
        li = xbmcgui.ListItem(label=item["title"])
        li.setArt({"poster": item.get("poster", ""), "fanart": item.get("fanart", "")})
        li.setInfo("video", {
            "title": item["title"],
            "plot": item.get("plot", ""),
            "year": item.get("year", ""),
            "genre": item.get("genres", ""),
        })
        if item.get("imdb_id"):
            li.setUniqueIDs({"imdb": item["imdb_id"]}, "imdb")
        xbmcplugin.addDirectoryItem(
            ADDON_HANDLE,
            build_url({
                "action": "streams",
                "type": item["type"],
                "imdb_id": item["imdb_id"],
                "title": item["title"],
            }),
            li, True
        )
    xbmcplugin.endOfDirectory(ADDON_HANDLE)


def list_streams(video_type, imdb_id, clean_title, season=None, episode=None):
    xbmcplugin.setContent(ADDON_HANDLE, "videos")

    # 1. Subtitles — correct path format matching subtitles.js:
    #    /api/subtitles/{type}/{imdb_id}.json
    #    /api/subtitles/series/{imdb_id}:{season}:{episode}.json
    subtitle_files = []
    try:
        if video_type == "series" and season and episode:
            sub_path = f"{imdb_id}:{season}:{episode}.json"
        else:
            sub_path = f"{imdb_id}.json"
        subs_data = api_get(f"{BASE_URL}/api/subtitles/{video_type}/{sub_path}")
        subtitle_files = [
            s["url"] for s in subs_data.get("subtitles", []) if s.get("url")
        ]
    except Exception as e:
        xbmc.log(f"Personal Addon - Subtitle fetch error: {e}", xbmc.LOGWARNING)

    # 2. Streams — kodi.js supports season/episode for series
    stream_url = (
        f"{BASE_URL}/api/kodi?userKey={get_active_token()}"
        f"&imdb_id={imdb_id}&type={video_type}"
    )
    if video_type == "series" and season and episode:
        stream_url += f"&season={season}&episode={episode}"

    try:
        data = api_get(stream_url, timeout=25)
    except Exception as e:
        show_error("שגיאת חיבור: " + str(e))
        return

    results = data.get("results", [])
    if not results:
        show_error("לא נמצאו מקורות עבור התוכן הזה")
        return

    for stream in results:
        quality = stream.get("quality", "SD")
        label = f"[{quality}] {clean_title}"
        if stream.get("sizeGB"):
            label += f" ({stream['sizeGB']} GB)"
        li = xbmcgui.ListItem(label=label)
        li.setInfo("video", {
            "title": clean_title,
            "plot": str(stream.get("title", ""))[:60],
        })
        li.setUniqueIDs({"imdb": imdb_id}, "imdb")
        li.setProperty("IsPlayable", "true")
        if subtitle_files:
            li.setSubtitles(subtitle_files)
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, stream["url"], li, False)

    xbmcplugin.endOfDirectory(ADDON_HANDLE)


# ==============================================================================
# Router
# ==============================================================================

def router():
    params = get_params()
    action = params.get("action")

    if not action:
        apply_skin_profile()  # Only on home screen
        list_root()
    elif action == "type_root":
        content_type = params.get("type", "movie")
        if content_type == "tv":
            list_live_tv_root()
        elif content_type == "anime":
            list_anime_root()
        else:
            list_type_root(content_type)
    elif action == "live_tv_kanbox":
        list_live_tv_kanbox()
    elif action == "roku_root":
        list_roku_root()
    elif action == "anime_genre_combo":
        list_anime_genre_combo(params["genres"])
    elif action == "catalog":
        list_catalog_items(params["type"], params["catalogId"])
    elif action == "streams":
        list_streams(
            params["type"],
            params["imdb_id"],
            params.get("title", "תוצאה"),
            season=params.get("season"),
            episode=params.get("episode"),
        )


if __name__ == "__main__":
    router()
