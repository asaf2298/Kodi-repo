# How to Package the Build ZIPs

OpenWizard restores a ZIP that maps directly onto the Kodi userdata folder.
The ZIP must physically contain ALL addons — OpenWizard does NOT install them.

## ZIP Internal Structure
```
personal-build-light-v1.0.zip
├── addons/
│   ├── plugin.video.personal/       ← from kodi-repo/plugin.video.personal/
│   │   ├── addon.xml
│   │   ├── main.py
│   │   ├── icon.png
│   │   └── resources/settings.xml
│   ├── script.trakt/                ← copy from working Kodi install
│   ├── script.module.requests/      ← copy from working Kodi install
│   ├── skin.arctic.zephyr.mod/      ← LIGHT only
│   └── script.openwizard/           ← so users can update later
│
└── userdata/
    ├── autoexec.py                  ← from build-shared/userdata/
    ├── shortcuts/
    │   └── mainmenu.DATA.xml        ← from build-shared/userdata/shortcuts/
    ├── addon_data/
    │   ├── plugin.video.personal/
    │   │   └── settings.xml         ← from build-light/userdata/addon_data/
    │   └── script.trakt/
    │       └── settings.xml         ← from build-light/userdata/addon_data/
    └── guisettings.xml              ← your existing guisettings.xml (set skin to zephyr.mod)

personal-build-heavy-v1.0.zip
└── (same structure, but with skin.arctic.horizon.2/ and build-heavy settings)
```

## Steps to Build the ZIP
1. On your working Kodi PC, locate: `%APPDATA%\Kodi\` (Windows) or `~/.kodi/` (Linux)
2. Copy `addons/script.trakt`, `addons/script.module.requests`, `addons/skin.arctic.zephyr.mod`
3. Add `plugin.video.personal/` from this repo
4. Add the `userdata/` files from `build-light/` or `build-heavy/` folders
5. ZIP everything and upload to `wizard/zips/personal-build-light-v1.0.zip`

## OpenWizard Manifest URL
```
https://raw.githubusercontent.com/asaf2298/Kodi-repo/main/wizard/builds.txt
```

## Why ActivateWindow Shortcuts Work Without Skin Configuration
The `mainmenu.DATA.xml` shortcuts use `ActivateWindow(Videos, "plugin://...")` which
bypasses the skin's menu picker entirely. The skin reads this file directly on load,
so the home menu is pre-configured the moment Kodi starts — no manual setup needed.
