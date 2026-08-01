# Kodi-repo

Personal Kodi build system for asaf2298. Generates two prebuilt Kodi packages (Light and Heavy) with pre-configured addons, skin, and userdata for one-click OpenWizard installation.

`plugin.video.personal`'s entire backend is `asaf2298/UserManager`'s `api/kodi.js` (stream resolution) and `api/kodi-catalog.js` (catalog browsing) -- see that repo's CLAUDE.md/AGENTS.md for the server side of every route referenced below.

## Structure

- `plugin.video.personal/` — Custom Kodi video addon (source of truth, always freshest version)
- `build-shared/` — userdata shared between both build profiles (autoexec.py, mainmenu.DATA.xml shortcuts)
- `build-light/` — userdata specific to Light profile (addon_data, guisettings.xml)
- `build-heavy/` — userdata specific to Heavy profile (performance settings only -- see Known Gotchas)
- `wizard/` — OpenWizard manifest (`builds.txt`) and packaged output ZIPs (`wizard/zips/`)
- `userdata/` — reference userdata used during packaging
- `package-from-here.ps1` — packaging script; run from inside a real Kodi `addons` folder, points to this repo for repo-specific files, outputs both ZIPs to Desktop
- `package-builds.ps1` — alternate/legacy packaging script

## Live TV (3 rows) and Anime (4 rows)

`list_live_tv_root()` in `main.py` builds three rows -- none of them reimplement stream resolution, all delegate:

1. **Kan-Box (Israeli)** -- `list_live_tv_kanbox()`, via `api/kodi-catalog?list=live_channels` (catalog) and `api/kodi?...&type=tv` (stream, proxies to `TV_ADDON_URL` server-side -- see UserManager's CLAUDE.md).
2. **Pluto TV US News** -- a direct `plugin://slyguy.pluto.tv.provider/?_=live_tv&code=us&group=News + Opinion` deep link (built via `build_external_url()`). "News + Opinion" is the real channel group tag from `i.mjh.nz/PlutoTV`'s `us` region data (confirmed live: 39 channels). Pluto TV has no Israeli region at all (checked `i.mjh.nz`'s real per-country file list: `ar,br,ca,cl,de,dk,es,fr,gb,it,mx,no,se,us` -- no `il`).
3. **Roku** -- `list_roku_root()`, a small folder with 2 deep links: `plugin://slyguy.roku/?_=live_tv` and `plugin://slyguy.roku/?_=search`, unfiltered (not news-specific, unlike Pluto). Roku Channel has no per-region split and no Israeli availability either.

`build_external_url(addon_id, route, **params)` replicates `script.module.slyguy`'s own `router.build_url()` encoding exactly (route name in the `_` param, then all params `urlencode`d together sorted by key) -- verified against the real addon source (`script.module.slyguy/resources/modules/slyguy/router.py`) and against how each addon links to itself from its own home menu.

`list_anime_root()` builds 4 fixed genre-combo rows, **AnimeIL only, never Cinemeta** (Cinemeta's `genre=Animation` mixes in non-anime Western animation -- confirmed live, Cinemeta has no anime-specific catalog at all). Genres per row and order are fixed in `ANIME_GENRE_ROWS`:
1. Sci-Fi, Fantasy, Action, War, Adventure
2. Thriller, Mystery, Horror, Crime, Drama
3. Romance, Family, Comedy
4. Music, History, Sport, Short, Animation

Each row calls `api/kodi-catalog?list=anime_genres&genres=...` (UserManager side fans out one request per genre x per type since AnimeIL only accepts one genre per request, then merges by id).

## Build Process

1. Place `package-from-here.ps1` inside the actual Kodi `addons` folder (e.g. `%APPDATA%\Kodi\addons\`)
2. Run: `powershell -ExecutionPolicy Bypass -File .\package-from-here.ps1`
3. Script auto-detects Kodi root (one level up from `addons`), locates this repo clone (prompts if not found), copies shared addons + `plugin.video.personal` + userdata (`$HeavyOnly` is currently empty -- both profiles are fully shared on addon set)
4. Both ZIPs (`personal-build-light-v1.0.zip`, `personal-build-heavy-v1.0.zip`) are written to the Desktop

## Deploying New Builds

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
- Both Light and Heavy profiles use the same skin (`skin.arctic.zephyr.mod`) and, as of the Pluto/Roku move to `$SharedAddons`, the same addon set. They differ only in performance settings (`LowPowerMode`, widget counts, etc. in each profile's `guisettings.xml`/skin settings).
- `slyguy.pluto.tv.provider` / `slyguy.roku`'s actual live-channel stream URLs are **not** in any static file anywhere -- they're resolved dynamically by those real addons at play time. Do not try to reimplement this; always deep-link into the real addon's own routes (see `build_external_url()` above). Their internal routing (`live_tv(code, group)`, `search(query)`) was confirmed by extracting the real addon zips from `matthuisman/slyguy.addons` and reading `resources/lib/plugin.py` directly -- do the same before assuming a route/param name.

## OpenWizard Manifest (`wizard/builds.txt`)

**Field order matters and is easy to get wrong.** OpenWizard (`a4k-openproject/plugin.program.openwizard`, `resources/libs/check.py: check_build()`) parses each `<build>` block with a single regex chain that requires fields to appear, after `name=`, in this **exact order**:
`version, url, minor, gui, kodi, theme, icon, fanart, preview, adult, info, description`.
Newlines/tabs are stripped from the whole file before matching, and it is a single global match across all `<build>` blocks concatenated together -- if the order is wrong, `check_build()` silently returns `False` for every field (no exception, no obvious error), which then makes `wizard.py`'s install flow show a bogus "version False" warning and fail to download (`buildzip = False`), aborting silently on the zero-byte-file check. This was found broken (this exact way) and fixed in this repo's history -- **always verify a field-order change by replicating the real regex from `check.py` against the actual file before pushing**, not just by eye.

`minor` and `gui` must be present even when unused. Only `gui=""` and `theme=""` are special-cased by OpenWizard itself (rewritten to `"http://"` internally) to survive being empty -- `minor=""` is **not** special-cased and breaks the capture group (`(.+?)` requires 1+ characters), so use a real placeholder (`minor="0"`) instead of an empty string.

`theme=` (when set) must point to a **parseable theme-list manifest** (matching `name="..."` entries, checked by `BuildMenu().theme_count()`), not a raw `.zip` -- a prior version of this file pointed `theme=` at a `wizard/theme.zip` that both didn't exist (404) and wasn't the right format either way. Currently set to `theme=""` (no extra theme package) since there's no such manifest built. A missing/invalid theme is harmless either way -- `theme_count()` returns 0 and the theme-install sub-step is silently skipped without blocking the rest of the build install.

Assets actually needed to exist for the manifest to work end-to-end: `icon.png`, `fanart.jpg`, `preview-light.jpg`, `preview-heavy.jpg`, and both changelog files under `wizard/changelogs/` -- `theme.zip` is not needed anymore.
