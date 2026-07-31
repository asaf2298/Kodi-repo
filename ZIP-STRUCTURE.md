# How to Package the Build ZIPs

OpenWizard restores a ZIP that maps directly onto your Kodi root folder.
**The ZIP must physically contain ALL addons** — OpenWizard does NOT install them from repos.

---

## Which Addons to Include

### ✅ Include from your working Kodi `addons/` folder (Folder 2)
These are YOUR build addons — copy all of them:

| Addon folder | Purpose | Light | Heavy |
|---|---|---|---|
| `plugin.video.personal/` | Main addon (from this repo) | ✅ | ✅ |
| `plugin.program.iptv.merge/` | Live TV channel merging | ✅ | ✅ |
| `plugin.program.openwizard/` | Build updater | ✅ | ✅ |
| `plugin.video.themoviedb.helper/` | Metadata + artwork | ✅ | ✅ |
| `plugin.video.tvnz.ondemand/` | VOD provider | ✅ | ✅ |
| `script.embuary.helper/` | Skin helper | ✅ | ✅ |
| `script.globalsearch/` | Global search | ✅ | ✅ |
| `script.module.simplecache/` | Dependency | ✅ | ✅ |
| `script.module.slyguy/` | SlyGuy dependency | ✅ | ✅ |
| `script.skinshortcuts/` | ⚠️ **CRITICAL** — powers mainmenu shortcuts | ✅ | ✅ |
| `script.trakt/` | Watch history sync | ✅ | ✅ |
| `skin.arctic.zephyr.mod/` | Skin for both builds | ✅ | ✅ |
| `skin.estuary/` | Fallback skin | ✅ | ✅ |
| `slyguy.pluto.tv.provider/` | Pluto TV streams | optional | ✅ |
| `slyguy.roku/` | Roku streams | optional | ✅ |

### ❌ Do NOT include (Folder 1 — Kodi built-ins)
These come pre-installed with every Kodi installation. Including them wastes space:
`metadata.*`, `peripheral.*`, `repository.xbmc.org`, `resource.*`, `screensaver.*`,
`script.module.pil`, `service.xbmc.versioncheck`, `webinterface.default`,
`xbmc.addon`, `xbmc.core`, `xbmc.gui`, `xbmc.json`, `xbmc.metadata`,
`xbmc.python`, `xbmc.webinterface`

---

## Skin Note
> Both Light and Heavy builds use **`skin.arctic.zephyr.mod`** (Arctic: Zephyr — Reloaded).
> The skin has **built-in Light and Heavy performance modes** in its own settings.
> Arctic Horizon 2 (`skin.arctic.horizon.2`) is **archived since Oct 2024** — do not use.

---

## ZIP Internal Structure
```
personal-build-light-v1.0.zip  (or heavy)
├── addons/
│   ├── plugin.video.personal/         ← from kodi-repo/plugin.video.personal/
│   ├── plugin.program.iptv.merge/
│   ├── plugin.program.openwizard/
│   ├── plugin.video.themoviedb.helper/
│   ├── plugin.video.tvnz.ondemand/
│   ├── script.embuary.helper/
│   ├── script.globalsearch/
│   ├── script.module.simplecache/
│   ├── script.module.slyguy/
│   ├── script.skinshortcuts/          ← CRITICAL for home menu shortcuts
│   ├── script.trakt/
│   ├── skin.arctic.zephyr.mod/        ← both builds, set mode in skin settings
│   ├── skin.estuary/
│   ├── slyguy.pluto.tv.provider/      ← heavy only (optional for light)
│   └── slyguy.roku/                   ← heavy only (optional for light)
│
└── userdata/
    ├── autoexec.py                    ← build-shared/userdata/autoexec.py
    ├── shortcuts/
    │   └── mainmenu.DATA.xml            ← build-shared/userdata/shortcuts/
    ├── addon_data/
    │   ├── plugin.video.personal/
    │   │   └── settings.xml             ← build-light/ or build-heavy/
    │   └── script.trakt/
    │       └── settings.xml             ← build-light/ or build-heavy/
    └── guisettings.xml                ← your existing file (skin set to arctic.zephyr.mod)
```

---

## Steps to Build the ZIP

1. On your working Kodi PC open: `%APPDATA%\Kodi\` (Windows) or `~/.kodi/` (Linux)
2. Copy all addon folders listed in the ✅ table above from `addons/`
3. Copy `plugin.video.personal/` from **this repo** (always use the latest version)
4. Copy `userdata/` files from the matching `build-light/` or `build-heavy/` folder in this repo
5. Copy `build-shared/userdata/autoexec.py` and `shortcuts/mainmenu.DATA.xml`
6. Copy your `guisettings.xml` (make sure skin is set to `skin.arctic.zephyr.mod`)
7. ZIP the `addons/` and `userdata/` folders together
8. Upload the ZIP to `wizard/zips/personal-build-light-v1.0.zip` (or heavy)

---

## OpenWizard Manifest URL
```
https://raw.githubusercontent.com/asaf2298/Kodi-repo/main/wizard/builds.txt
```

---

## Why ActivateWindow Shortcuts Bypass the Skin
The `mainmenu.DATA.xml` shortcuts use `ActivateWindow(Videos, "plugin://...")` which
bypasses the skin’s menu picker entirely. `script.skinshortcuts` reads this file on
every Kodi start, so the home menu is pre-configured automatically — no manual setup needed.
