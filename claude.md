# Kodi-repo

Personal Kodi build system for asaf2298. Generates two prebuilt Kodi packages (Light and Heavy) with pre-configured addons, skin, and userdata for one-click OpenWizard installation.

## Structure

- `plugin.video.personal/` — Custom Kodi video addon (source of truth, always freshest version)
- `build-shared/` — userdata shared between both build profiles (autoexec.py, mainmenu.DATA.xml shortcuts)
- `build-light/` — userdata specific to Light profile (addon_data, guisettings.xml)
- `build-heavy/` — userdata specific to Heavy profile (adds slyguy.pluto.tv.provider, slyguy.roku)
- `wizard/` — OpenWizard manifest (`builds.txt`) and packaged output ZIPs (`wizard/zips/`)
- `userdata/` — reference userdata used during packaging
- `package-from-here.ps1` — packaging script; run from inside a real Kodi `addons` folder, points to this repo for repo-specific files, outputs both ZIPs to Desktop
- `package-builds.ps1` — alternate/legacy packaging script

## Build Process

1. Place `package-from-here.ps1` inside the actual Kodi `addons` folder (e.g. `%APPDATA%\Kodi\addons\`)
2. Run: `powershell -ExecutionPolicy Bypass -File .\package-from-here.ps1`
3. Script auto-detects Kodi root (one level up from `addons`), locates this repo clone (prompts if not found), copies shared addons + heavy-only addons + `plugin.video.personal` + userdata
4. Both ZIPs (`personal-build-light-v1.0.zip`, `personal-build-heavy-v1.0.zip`) are written to the Desktop

## Deploying New Builds

After running the packaging script:
```powershell
git add wizard/zips/personal-build-light-v1.0.zip wizard/zips/personal-build-heavy-v1.0.zip
git commit -m "Add build ZIPs"
git push origin main
```
Note: GitHub's web drag-and-drop uploader caps at 25MB — always push via git CLI for these ZIPs (up to 100MB each).

## Known Gotchas

- PowerShell does NOT support `\` as a line-continuation character — use full statements on one line or backtick `` ` `` only.
- `$ErrorActionPreference = "Stop"` will silently kill the whole script on any error — prefer `"Continue"` with explicit error checks.
- The repo root passed to the script must contain `plugin.video.personal`, `build-shared`, `build-light`, and `build-heavy` — never point it at the Kodi `addons` folder itself.
- Git identity must be configured once per machine: `git config --global user.email "..."` and `git config --global user.name "..."`.

## OpenWizard Manifest

`wizard/builds.txt` lists build metadata pointing to `wizard/zips/*.zip`. Both ZIPs must be present in that path (or migrated to GitHub Releases) for the wizard install flow to work.