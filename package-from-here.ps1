# package-from-here.ps1
# -----------------------------------------------------------------------
# INSTRUCTIONS:
#   1. Copy this file into your Kodi ADDONS folder
#      e.g.  D:\Kodi\addons\   or   E:\MyKodi\addons\
#   2. Right-click it -> "Run with PowerShell"
#   3. Both ZIPs will be saved to your Desktop
# -----------------------------------------------------------------------

param([string]$Version = "1.0")
$ErrorActionPreference = "Stop"

function OK($m)   { Write-Host "  [OK] $m" -ForegroundColor Green }
function WARN($m) { Write-Host "  [!!] $m" -ForegroundColor Yellow }
function INFO($m) { Write-Host "  --> $m" -ForegroundColor Cyan }
function HEAD($m) { Write-Host "`n$m" -ForegroundColor White }
function ERR($m)  { Write-Host "`n  [X] $m" -ForegroundColor Red; Read-Host "Press Enter to exit"; exit 1 }

HEAD "Personal Kodi Build Packager"

# ── Detect paths from THIS script's location (inside addons/) ──────────────
$AddonsDir   = $PSScriptRoot                    # the addons folder this script is in
$KodiRoot    = Split-Path $AddonsDir -Parent    # one level up = Kodi root
$UserDataDir = Join-Path $KodiRoot "userdata"   # Kodi/userdata
$RepoDir     = $PSScriptRoot                    # repo files expected alongside addons

INFO "Detected Kodi root : $KodiRoot"
INFO "Addons folder      : $AddonsDir"

if (-not (Test-Path $UserDataDir)) {
  ERR "Could not find userdata folder at: $UserDataDir`nMake sure this script is inside your Kodi addons folder."
}
OK "Kodi userdata found."

# ── Find the cloned repo (looks next to Kodi root, or prompts) ────────────
$RepoCandidates = @(
  (Join-Path (Split-Path $KodiRoot -Parent) "kodi-repo"),
  (Join-Path $env:USERPROFILE "kodi-repo"),
  (Join-Path $env:USERPROFILE "Desktop\kodi-repo"),
  (Join-Path $env:USERPROFILE "Documents\kodi-repo")
)
$RepoRoot = $null
foreach ($c in $RepoCandidates) {
  if (Test-Path (Join-Path $c "plugin.video.personal")) {
    $RepoRoot = $c; break
  }
}
if (-not $RepoRoot) {
  Write-Host ""
  WARN "Could not auto-find the kodi-repo clone."
  $RepoRoot = Read-Host "  Enter full path to your kodi-repo folder"
  if (-not (Test-Path (Join-Path $RepoRoot "plugin.video.personal"))) {
    ERR "plugin.video.personal not found in: $RepoRoot"
  }
}
OK "Repo root: $RepoRoot"

# ── Addon lists ─────────────────────────────────────────────────────────
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
$HeavyOnly = @(
  "slyguy.pluto.tv.provider",
  "slyguy.roku"
)

# ── Build function ─────────────────────────────────────────────────────────────────
function Build-Zip($profile) {
  HEAD "Building [$($profile.ToUpper())] ZIP..."
  $tmp = Join-Path $env:TEMP "kodi-personal-$profile"
  if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
  New-Item -ItemType Directory "$tmp\addons"   | Out-Null
  New-Item -ItemType Directory "$tmp\userdata" | Out-Null

  # 1. Shared addons from THIS addons folder
  HEAD "  [1/5] Copying shared addons..."
  foreach ($a in $SharedAddons) {
    $src = Join-Path $AddonsDir $a
    if (Test-Path $src) {
      Copy-Item $src "$tmp\addons\$a" -Recurse; OK $a
    } else {
      WARN "$a not found — skipped"
    }
  }

  # 2. Heavy-only addons
  if ($profile -eq "heavy") {
    HEAD "  [2/5] Copying heavy-only addons..."
    foreach ($a in $HeavyOnly) {
      $src = Join-Path $AddonsDir $a
      if (Test-Path $src) {
        Copy-Item $src "$tmp\addons\$a" -Recurse; OK $a
      } else {
        WARN "$a not found — skipped"
      }
    }
  }

  # 3. plugin.video.personal from REPO (always freshest version)
  HEAD "  [3/5] Copying plugin.video.personal from repo..."
  Copy-Item (Join-Path $RepoRoot "plugin.video.personal") "$tmp\addons\plugin.video.personal" -Recurse
  OK "plugin.video.personal (repo version)"

  # 4. Shared userdata (autoexec.py + shortcuts)
  HEAD "  [4/5] Copying shared userdata..."
  Copy-Item (Join-Path $RepoRoot "build-shared\userdata\autoexec.py") "$tmp\userdata\autoexec.py"
  OK "autoexec.py"
  New-Item -ItemType Directory "$tmp\userdata\shortcuts" -Force | Out-Null
  Copy-Item (Join-Path $RepoRoot "build-shared\userdata\shortcuts\mainmenu.DATA.xml") \
            "$tmp\userdata\shortcuts\mainmenu.DATA.xml"
  OK "mainmenu.DATA.xml"

  # 5. Profile-specific userdata (addon_data + guisettings)
  HEAD "  [5/5] Copying profile userdata..."
  $profileUD = Join-Path $RepoRoot "build-$profile\userdata"
  Copy-Item (Join-Path $profileUD "addon_data") "$tmp\userdata\addon_data" -Recurse
  OK "addon_data/"
  Copy-Item (Join-Path $profileUD "guisettings.xml") "$tmp\userdata\guisettings.xml"
  OK "guisettings.xml"

  # 6. ZIP to Desktop
  $zipName = "personal-build-$profile-v$Version.zip"
  $zipPath = Join-Path ([Environment]::GetFolderPath("Desktop")) $zipName
  if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
  Compress-Archive -Path "$tmp\*" -DestinationPath $zipPath
  $sizeMB = [math]::Round((Get-Item $zipPath).Length / 1MB, 1)
  OK "Saved to Desktop: $zipName ($sizeMB MB)"

  Remove-Item $tmp -Recurse -Force
  return $zipPath
}

# ── Run ─────────────────────────────────────────────────────────────────────────
Build-Zip "light"
Build-Zip "heavy"

HEAD "✅ Done! Both ZIPs are on your Desktop."
Write-Host ""
Write-Host "  Next: upload them to GitHub at:" -ForegroundColor Cyan
Write-Host "  kodi-repo/wizard/zips/" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
