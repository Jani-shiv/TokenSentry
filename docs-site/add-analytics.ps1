$files = Get-ChildItem *.html
foreach ($f in $files) {
    $content = Get-Content $f -Raw
    if ($content -notmatch '_vercel/insights/script\.js') {
        $content = $content -replace '(<link rel="stylesheet" href="styles/brutal\.css">)', '$1`n  <!-- Vercel Web Analytics -->`n  <script defer src="/_vercel/insights/script.js"></script>'
        Set-Content $f -Value $content -Encoding UTF8
        Write-Host "Updated $($f.Name)"
    } else {
        Write-Host "Already has analytics: $($f.Name)"
    }
}