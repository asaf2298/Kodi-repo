# package-builds.ps1 — Personal Kodi Build Auto-Packager
# Run from the root of this repo on your Windows machine with Kodi installed.
# Produces: wizard/zips/personal-build-light-v1.0.zip
#           wizard/zips/personal-build-heavy-v1.0.zip

param(
  [string]$KodiPath = "",
  [string]$Version  = "1.0"
)

$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot

# ── Colors ──────────────────────────────────────────────────────────────────
function OK($m)   { Write-Host "  [OK] $m" -ForegroundColor Green }
function WARN($m) { Write-Host "  [!!] $m" -ForegroundColor Yellow }
function INFO($m) { Write-Host "  --> $m" -ForegroundColor Cyan }
function HEAD($m) { Write-Host "`n$m" -ForegroundColor White }
function ERR($m)  { Write-Host "  [X] $m" -ForegroundColor Red; exit 1 }

HEAD "Personal Kodi Build Packager v$Version"
INFO "Repo: $RepoRoot"

# ── Find Kodi root ─────────────────────────────────────────────────────────────
if (-not $KodiPath) {
  $candidates = @(
    "$env:APPDATA\Kodi",
    "C:\Kodi",
    "$env:LOCALAPPDATA\Kodi"
  )
  foreach ($c in $candidates) {
    if (Test-Path "$c\userdata") { $KodiPath = $c; break }
  }
}
if (-not $KodiPath -or -not (Test-Path "$KodiPath\userdata")) {
  ERR "Cannot find Kodi folder. Run: .\package-builds.ps1 -KodiPath 'C:\path\to\Kodi'"
}
OK "Kodi root: $KodiPath"
$KodiAddons   = "$KodiPath\addons"
$KodiUserdata = "$KodiPath\userdata"

# ── Addons to include in BOTH builds ──────────────────────────────────────────────
$SharedAddons = @(
  "plugin.program.iptv.merge",
  "plugin.program.openwizard",
  "plugin.video.themoviedb.helper",
  "plugin.video.tvnz.ondemand",
  "script.embuary.helper",
  "script.globalsearch",
  "script.module.simplecache",
  "script.module.slyguy",
  "script.skinshortcuts",
  "script.trakt",
  "skin.arctic.zephyr.mod",
  "skin.estuary"
)

$HeavyOnlyAddons = @(
  "slyguy.pluto.tv.provider",
  "slyguy.roku"
)

# ── Build function ───────────────────────────────────────────────────────────────────
function Build-Zip {
  param([string]$Profile)

  HEAD "[$($Profile.ToUpper())] Building..."
  $TempDir = Join-Path $env:TEMP "kodi-build-$Profile"
  if (Test-Path $TempDir) { Remove-Item $TempDir -Recurse -Force }
  New-Item -ItemType Directory -Path "$TempDir\addons" | Out-Null
  New-Item -ItemType Directory -Path "$TempDir\userdata" | Out-Null

  # 1. Copy shared addons from Kodi installation
  HEAD "  [1] Copying shared addons..."
  foreach ($addon in $SharedAddons) {
    $src = "$KodiAddons\$addon"
    if (Test-Path $src) {
      Copy-Item $src "$TempDir\addons\$addon" -Recurse
      OK $addon
    } else {
      WARN "$addon NOT FOUND in Kodi addons — skipping"
    }
  }

  # 2. Heavy-only addons
  if ($Profile -eq "heavy") {
    HEAD "  [2] Copying heavy-only addons..."
    foreach ($addon in $HeavyOnlyAddons) {
      $src = "$KodiAddons\$addon"
      if (Test-Path $src) {
        Copy-Item $src "$TempDir\addons\$addon" -Recurse
        OK $addon
      } else {
        WARN "$addon NOT FOUND — skipping"
      }
    }
  }

  # 3. Copy plugin.video.personal from THIS REPO (always latest)
  HEAD "  [3] Copying plugin.video.personal from repo..."
  $pvpSrc = "$RepoRoot\plugin.video.personal"
  if (Test-Path $pvpSrc) {
    Copy-Item $pvpSrc "$TempDir\addons\plugin.video.personal" -Recurse
    OK "plugin.video.personal (from repo)"
  } else {
    ERR "plugin.video.personal not found in repo root!"
  }

  # 4. Copy shared userdata files
  HEAD "  [4] Copying shared userdata..."
  $sharedUD = "$RepoRoot\build-shared\userdata"
  Copy-Item "$sharedUD\autoexec.py" "$TempDir\userdata\autoexec.py"
  OK "autoexec.py"
  New-Item -ItemType Directory -Path "$TempDir\userdata\shortcuts" -Force | Out-Null
  Copy-Item "$sharedUD\shortcuts\mainmenu.DATA.xml" "$TempDir\userdata\shortcuts\mainmenu.DATA.xml"
  OK "shortcuts/mainmenu.DATA.xml"

  # 5. Copy profile-specific userdata (addon_data + guisettings)
  HEAD "  [5] Copying $Profile profile userdata..."
  $profileUD = "$RepoRoot\build-$Profile\userdata"

  # addon_data
  $addonDataSrc = "$profileUD\addon_data"
  if (Test-Path $addonDataSrc) {
    Copy-Item $addonDataSrc "$TempDir\userdata\addon_data" -Recurse
    OK "addon_data/"
  }

  # guisettings.xml (from repo, pre-configured per profile)
  $guiSrc = "$profileUD\guisettings.xml"
  if (Test-Path $guiSrc) {
    Copy-Item $guiSrc "$TempDir\userdata\guisettings.xml"
    OK "guisettings.xml"
  }

  # 6. ZIP it
  HEAD "  [6] Packaging ZIP..."
  $ZipDir = "$RepoRoot\wizard\zips"
  if (-not (Test-Path $ZipDir)) { New-Item -ItemType Directory -Path $ZipDir | Out-Null }
  $ZipPath = "$ZipDir\personal-build-$Profile-v$Version.zip"
  if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }
  Compress-Archive -Path "$TempDir\*" -DestinationPath $ZipPath
  OK "Created: $ZipPath"

  # Cleanup
  Remove-Item $TempDir -Recurse -Force
  INFO "ZIP size: $([math]::Round((Get-Item $ZipPath).Length / 1MB, 1)) MB"
}

# ── Run both builds ───────────────────────────────────────────────────────────────────
Build-Zip -Profile "light"
Build-Zip -Profile "heavy"

HEAD "✅ Both ZIPs ready!"
Write-Host ""
Write-Host "  wizard/zips/personal-build-light-v$Version.zip" -ForegroundColor Green
Write-Host "  wizard/zips/personal-build-heavy-v$Version.zip" -ForegroundColor Green
Write-Host ""
Write-Host "  Upload both ZIPs to GitHub, then share the OpenWizard URL:" -ForegroundColor Cyan
Write-Host "  https://raw.githubusercontent.com/asaf2298/Kodi-repo/main/wizard/builds.txt" -ForegroundColor Cyan
Write-Host ""
