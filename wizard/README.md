# OpenWizard Build Manifest

## Setup in OpenWizard
1. Open OpenWizard → Builds → Add Source
2. Paste this URL:
   ```
   https://raw.githubusercontent.com/asaf2298/Kodi-repo/main/wizard/builds.txt
   ```
3. Choose **Light System Build** or **Heavy System Build**
4. Install and restart Kodi
5. On first boot, Trakt authorization triggers automatically

## Build ZIPs
ZIP files need to be uploaded to:
```
wizard/zips/personal-build-light-v1.0.zip
wizard/zips/personal-build-heavy-v1.0.zip
```

## ZIP Contents Structure
Each ZIP should contain:
```
addons/
  plugin.video.personal/
    addon.xml
    main.py
    icon.png
    resources/
      settings.xml
userdata/
  autoexec.py
  guisettings.xml        ← pre-configured for each profile
  addon_data/
    plugin.video.personal/
      settings.xml       ← pre-set system_profile to 0 (light) or 1 (heavy)
```

## Manifest URL (share this with users)
```
https://raw.githubusercontent.com/asaf2298/Kodi-repo/main/wizard/builds.txt
```
