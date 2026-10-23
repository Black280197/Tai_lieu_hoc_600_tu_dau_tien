param([string]$File)

$lines = Get-Content -Encoding UTF8 $File
$idx = @()
for ($i = 0; $i -lt $lines.Count; $i++) {
  if ($lines[$i] -match '^### ') { $idx += $i }
}
for ($k = 0; $k -lt $idx.Count; $k++) {
  $start = $idx[$k]
  $end = if ($k + 1 -lt $idx.Count) { $idx[$k + 1] - 1 } else { $lines.Count - 1 }
  $block = $lines[$start..$end]
  $need = @('**Nét vẽ chữ', '**Bóc tách thành phần từng chữ**', '**Nguồn gốc & Bản chất từng chữ**', '**Nguồn gốc & Bản chất của từ / cụm từ**', '**Hình ảnh liên tưởng', '**Ngữ cảnh sử dụng')
  $miss = @()
  foreach ($n in $need) {
    $found = $false
    foreach ($b in $block) { if ($b.TrimStart().StartsWith($n)) { $found = $true; break } }
    if (-not $found) { $miss += $n }
  }
  $q = ($block | Where-Object { $_ -match '^> \*' }).Count
  $dn = ($block | Where-Object { $_ -match 'Dịch nghĩa:' }).Count
  if ($miss.Count -gt 0 -or $q -ne 1 -or $dn -ne 2) {
    '{0} | thieu: {1} | quote={2} | dich={3}' -f $lines[$start], ($miss -join ';'), $q, $dn
  }
}
'=== XONG ==='
