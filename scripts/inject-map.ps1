$ErrorActionPreference = 'Stop'
$mapPath  = 'C:\Users\jonas\Desktop\AI Data\Projekt Henne\europe-map.svg'
$htmlPath = 'C:\Users\jonas\Desktop\AI Data\Projekt Henne\chicken-dashboard.html'

$map = [System.IO.File]::ReadAllText($mapPath)
$svgOpen = $map.IndexOf('<svg')
if ($svgOpen -lt 0) { throw 'No <svg> found in map file' }
$start = $map.IndexOf('>', $svgOpen) + 1
$end   = $map.LastIndexOf('</svg>')
$inner = $map.Substring($start, $end - $start)

$html = [System.IO.File]::ReadAllText($htmlPath)
$placeholder = '<!--EUROPE_MAP_PATHS-->'
if (-not $html.Contains($placeholder)) { throw 'Placeholder not found in HTML' }

$html = $html.Replace($placeholder, $inner)
$utf8 = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($htmlPath, $html, $utf8)

Write-Output ("Injected " + $inner.Length + " chars of map path data.")
