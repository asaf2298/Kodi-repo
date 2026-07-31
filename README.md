# Personal Kodi Build — plugin.video.personal

## Quick Install (Automated)
```bash
# Windows — double-click or run:
python install.py

# Linux / macOS
./install.sh

# Install a specific profile directly
python install.py light
python install.py heavy
```
The installer auto-detects your Kodi userdata path on Windows, macOS, Linux, LibreELEC, and Android.

## OpenWizard Manifest URL
For OpenWizard-based installs, add this source:
```
https://raw.githubusercontent.com/asaf2298/Kodi-repo/main/wizard/builds.txt
```

## Repo Structure
```
kodi-repo/
├── plugin.video.personal/         → main addon
├── build-shared/userdata/
│   ├── autoexec.py                → Trakt auth + addon check on boot
│   └── shortcuts/
│       └── mainmenu.DATA.xml       → home menu shortcuts (bypasses skin picker)
├── build-light/userdata/addon_data/
│   ├── plugin.video.personal/settings.xml  → profile=0 (light token)
│   └── script.trakt/settings.xml            → 8 public Trakt lists
├── build-heavy/userdata/addon_data/
│   ├── plugin.video.personal/settings.xml  → profile=1 (heavy token)
│   └── script.trakt/settings.xml            → 11 public Trakt lists
├── wizard/
│   ├── builds.txt                 → OpenWizard manifest
│   └── changelogs/
├── install.py                     → automated installer
├── install.bat                    → Windows one-click
├── install.sh                     → Linux/macOS one-click
└── ZIP-STRUCTURE.md               → how to package build ZIPs
```

## Build Profiles

| Feature | Light | Heavy |
|---|---|---|
| **Token** | `123kodi123token123friend_light` | `123kodi123token123everything` |
| **Backend profile** | `friends_light` (10 streams, 30GB cap) | `everything` (30 streams, unlimited) |
| **Skin** | `skin.arctic.zephyr.mod` | `skin.arctic.zephyr.mod` |
| **Skin mode** | Low-power / Light mode in skin settings | Full / Heavy mode in skin settings |
| **Target devices** | Android TV, FireStick | PC, Nvidia Shield |
| **Trakt lists** | 8 public lists | 11 public lists |

> Both builds use **Arctic: Zephyr — Reloaded** (`skin.arctic.zephyr.mod`).
> Arctic Horizon 2 is archived (Oct 2024) and no longer recommended.
> The skin has built-in Light/Heavy performance modes in its own settings.

## Backend API
| Endpoint | URL |
|---|---|
| Streams | `/api/kodi?userKey=...&imdb_id=...&type=...` |
| Catalog | `/api/kodi-catalog?userKey=...&list=catalogs` |
| Live TV | `/api/kodi-catalog?userKey=...&list=live_channels` |
| Subtitles (movie) | `/api/subtitles/movie/{imdb_id}.json` |
| Subtitles (series) | `/api/subtitles/series/{imdb_id}:{season}:{episode}.json` |

Base URL: `https://user-manager-lime.vercel.app`

## Pre-configured Trakt Public Lists
| # | List | Light | Heavy |
|---|---|---|---|
| 1 | Trending Movies | ✅ | ✅ |
| 2 | Trending Shows | ✅ | ✅ |
| 3 | Popular Movies | ✅ | ✅ |
| 4 | Popular Shows | ✅ | ✅ |
| 5 | Best Movies of 2024 | ✅ | ✅ |
| 6 | IMDb Top 250 Movies | ✅ | ✅ |
| 7 | IMDb Top Rated TV Shows | ✅ | ✅ |
| 8 | Anime Movies | ✅ | ✅ |
| 9 | Top Anime Series | — | ✅ |
| 10 | Oscar Best Picture Winners | — | ✅ |
| 11 | Box Office Hits | — | ✅ |

## Home Menu Shortcuts
The `mainmenu.DATA.xml` file uses `ActivateWindow(Videos, "plugin://...")` to bypass
the skin menu picker entirely. Powered by `script.skinshortcuts` — **this addon must
be present in the ZIP** for shortcuts to work.

| Label | Action |
|---|---|
| שידור חי | `type=tv` |
| סרטים | `type=movie` |
| סדרות | `type=series` |
| אנימה | `type=anime` |
| מעקב צפייה | Trakt |
| הגדרות | Settings |
| כיבוי | Shutdown |
