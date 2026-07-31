# Personal Kodi Build — plugin.video.personal

## Folder Structure
```
kodi-repo/
├── plugin.video.personal/     → install as Kodi addon
│   ├── addon.xml
│   ├── main.py
│   ├── icon.png
│   └── resources/
│       └── settings.xml
└── userdata/
    └── autoexec.py            → copy to Kodi/userdata/
```

## Backend
| Endpoint | URL |
|---|---|
| Streams | `/api/kodi?userKey=...&imdb_id=...&type=...` |
| Catalog | `/api/kodi-catalog?userKey=...&list=catalogs` |
| Live TV | `/api/kodi-catalog?userKey=...&list=live_channels` |
| Subtitles (movie) | `/api/subtitles/movie/{imdb_id}.json` |
| Subtitles (series) | `/api/subtitles/series/{imdb_id}:{season}:{episode}.json` |

Base URL: `https://user-manager-lime.vercel.app`

## Installation
1. Download this repo as ZIP
2. In Kodi: Install from ZIP → select `plugin.video.personal/`
3. Copy `userdata/autoexec.py` to your Kodi userdata folder
4. Restart Kodi — Trakt auth triggers automatically on first boot

## Profiles
| Profile | Skin | Token |
|---|---|---|
| Light (default) | `skin.arctic.zephyr.mod` | light token |
| Heavy | `skin.arctic.horizon.2` | heavy token |

To override the user key: Add-on Settings → "User Key Override"
