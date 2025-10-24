<# 
Set-Timezone-From-IP.ps1  (v2.2)
- Detect public IP (multi-fallback) and print it
- Detect IANA timezone from public IP (multi-fallback JSON APIs)
- Map IANA -> Windows timezone id
- Set Windows timezone via tzutil
- Force Windows Time (NTP) resync to avoid SSL/time errors
Usage:
  powershell -ExecutionPolicy Bypass -File ".\Set-Timezone-From-IP.ps1"
  (Optional) -Iana "Europe/Zurich"  # bypass IP lookup
  (Optional) -NoResync              # skip NTP resync
  (Optional) -WhatIf                # show actions only
#>

[CmdletBinding()]
param(
  [string]$Iana = $null,         
  [switch]$NoResync,             
  [switch]$WhatIf                
)

function Write-Info($m){ Write-Host "[*] $m" -ForegroundColor Cyan }
function Write-Ok($m){ Write-Host "[+] $m" -ForegroundColor Green }
function Write-Warn($m){ Write-Host "[!] $m" -ForegroundColor Yellow }
function Write-Err($m){ Write-Host "[-] $m" -ForegroundColor Red }

function Invoke-JsonGet($url){
  try {
    $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 8 -ErrorAction Stop
    if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300) {
      return $r.Content | ConvertFrom-Json
    }
  } catch { return $null }
  return $null
}

function Invoke-TextGet($url){
  try {
    $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 8 -ErrorAction Stop
    if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300) {
      $t = ($r.Content).Trim()
      if ($t -match '^\d{1,3}(\.\d{1,3}){3}$' -or $t -match '^[0-9a-fA-F:]+$') { return $t }
    }
  } catch { return $null }
  return $null
}

# --- NEW: Get public IP (IPv4/IPv6), multiple fallbacks ---
function Get-PublicIP {
  $textEndpoints = @(
    "https://api.ipify.org", 
    "https://ifconfig.me/ip",
    "https://ipinfo.io/ip"
  )
  foreach($u in $textEndpoints){
    $ip = Invoke-TextGet $u
    if ($ip) { return $ip }
  }
  # Fallback via JSON endpoints
  $jsonEndpoints = @(
    @{ url = "https://ipapi.co/json";  field = "ip" },
    @{ url = "https://ipwho.is/";      field = "ip" },
    @{ url = "https://ipinfo.io/json"; field = "ip" }
  )
  foreach($e in $jsonEndpoints){
    $j = Invoke-JsonGet $e.url
    if ($j) {
      $ip = $j.($e.field)
      if ($ip) { return $ip }
    }
  }
  return $null
}

# Canonical IANA -> Windows mapping (extend as needed)
$ianaToWindows = @{
  # VN/SEA/ASIA
  "Asia/Ho_Chi_Minh"   = "SE Asia Standard Time"
  "Asia/Bangkok"       = "SE Asia Standard Time"
  "Asia/Jakarta"       = "SE Asia Standard Time"
  "Asia/Singapore"     = "Singapore Standard Time"
  "Asia/Kuala_Lumpur"  = "Singapore Standard Time"
  "Asia/Manila"        = "Singapore Standard Time"
  "Asia/Shanghai"      = "China Standard Time"
  "Asia/Taipei"        = "Taipei Standard Time"
  "Asia/Tokyo"         = "Tokyo Standard Time"
  "Asia/Seoul"         = "Korea Standard Time"
  "Asia/Kolkata"       = "India Standard Time"
  "Asia/Dhaka"         = "Bangladesh Standard Time"

  # EUROPE
  "Europe/London"      = "GMT Standard Time"
  "Europe/Dublin"      = "GMT Standard Time"
  "Europe/Zurich"      = "W. Europe Standard Time"
  "Europe/Berlin"      = "W. Europe Standard Time"
  "Europe/Vienna"      = "W. Europe Standard Time"
  "Europe/Amsterdam"   = "W. Europe Standard Time"
  "Europe/Stockholm"   = "W. Europe Standard Time"
  "Europe/Copenhagen"  = "W. Europe Standard Time"
  "Europe/Oslo"        = "W. Europe Standard Time"
  "Europe/Rome"        = "W. Europe Standard Time"
  "Europe/Prague"      = "Central Europe Standard Time"
  "Europe/Budapest"    = "Central Europe Standard Time"
  "Europe/Warsaw"      = "Central European Standard Time"
  "Europe/Paris"       = "Romance Standard Time"
  "Europe/Madrid"      = "Romance Standard Time"
  "Europe/Brussels"    = "Romance Standard Time"
  "Europe/Athens"      = "GTB Standard Time"
  "Europe/Helsinki"    = "FLE Standard Time"
  "Europe/Moscow"      = "Russian Standard Time"
  "Africa/Cairo"       = "Egypt Standard Time"
	
  # AMERICAS
  "America/Los_Angeles"= "Pacific Standard Time"
  "America/Vancouver"  = "Pacific Standard Time"
  "America/Denver"     = "Mountain Standard Time"
  "America/Chicago"    = "Central Standard Time"
  "America/New_York"   = "Eastern Standard Time"
  "America/Toronto"    = "Eastern Standard Time"
  "America/Sao_Paulo"  = "E. South America Standard Time"

  # AU/NZ
  "Australia/Sydney"   = "AUS Eastern Standard Time"
  "Australia/Melbourne"= "AUS Eastern Standard Time"
  "Australia/Perth"    = "W. Australia Standard Time"
  "Pacific/Auckland"   = "New Zealand Standard Time"
}

# Return both IANA and IP from JSON sources (if available)
function Get-IanaFromIP {
  $sources = @(
    @{ url = "https://ipapi.co/json";      field = "timezone"; ipfield = "ip" },
    @{ url = "https://ipinfo.io/json";     field = "timezone"; ipfield = "ip" },
    @{ url = "https://ipwho.is/";          field = "timezone"; ipfield = "ip" }
  )
  foreach ($s in $sources) {
    $j = Invoke-JsonGet $s.url
    if ($j) {
      $iana = $j.($s.field)
      $ip   = $j.($s.ipfield)
      if ($iana -and $iana -match "/") { 
        return [PSCustomObject]@{ Iana = $iana; IP = $ip } 
      }
    }
  }
  return $null
}

function Convert-IanaToWindows([string]$iana) {
  if (-not $iana) { return $null }
  if ($ianaToWindows.ContainsKey($iana)) { return $ianaToWindows[$iana] }
  return $null
}

# ---------------- Main flow ----------------
$publicIP = Get-PublicIP
if ($publicIP) { Write-Ok ("Public IP: {0}" -f $publicIP) } else { Write-Warn "Could not detect public IP (non-fatal)." }

if (-not $Iana) {
  Write-Info "Detecting timezone from public IP..."
  $tz = Get-IanaFromIP
  if (-not $tz) { Write-Err "Could not retrieve timezone from IP (APIs blocked or offline)."; exit 1 }
  if (-not $publicIP -and $tz.IP) {
    $publicIP = $tz.IP
    Write-Ok ("Public IP (from JSON): {0}" -f $publicIP)
  }
  $Iana = $tz.Iana
}
Write-Ok ("IANA timezone: {0}" -f $Iana)

$win = Convert-IanaToWindows $Iana
if (-not $win) {
  Write-Err ("No Windows mapping for {0}. Please add to `$ianaToWindows in the script." -f $Iana)
  exit 1
}

if ($WhatIf) {
  Write-Info ('[WhatIf] Would run: tzutil /s "{0}"' -f $win)
} else {
  try {
    & tzutil /s "$win" | Out-Null
    if ($LASTEXITCODE -eq 0) {
      $cur = (& tzutil /g)
      Write-Ok ("Windows timezone set to: {0}" -f $cur)
    } else {
      Write-Err ("tzutil returned code {0}" -f $LASTEXITCODE)
      exit $LASTEXITCODE
    }
  } catch {
    Write-Err ("Failed to set timezone: {0}" -f $_.Exception.Message)
    exit 1
  }
}

# ----- Force re-sync system time (NTP) unless disabled -----
if (-not $NoResync) {
  Write-Info "Resyncing Windows time service..."
  try {
    sc.exe config w32time start= auto | Out-Null
    net start w32time | Out-Null
  } catch {}
  try {
    w32tm /resync /force | Out-Null
    Start-Sleep -Seconds 2
    $status = (w32tm /query /status 2>$null) -join "`n"
    if ($status) {
      Write-Ok "System clock re-synced."
      Write-Info ($status -split "`n" | Select-Object -First 4 | Out-String)
    } else {
      Write-Warn "Resync requested, but status not available (non-fatal)."
    }
  } catch {
    Write-Warn "Could not resync automatically. Please enable 'Set time automatically' or check firewall."
  }
} else {
  Write-Info "Skip time resync as requested (--NoResync)."
}
