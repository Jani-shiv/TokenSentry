$ga = @"
  <!-- Google Analytics -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-VD5JW3RX34"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-VD5JW3RX34');
  </script>
"@

$files = Get-ChildItem *.html
foreach ($f in $files) {
    $content = Get-Content $f -Raw
    if ($content -notmatch 'G-VD5JW3RX34') {
        $pattern = '<script defer src="/_vercel/insights/script\.js"></script>'
        $replacement = $pattern + "`n" + $ga
        $content = $content -replace [regex]::Escape($pattern), $replacement
        Set-Content $f -Value $content -Encoding UTF8
        Write-Host "Added GA to $($f.Name)"
    } else {
        Write-Host "GA already in $($f.Name)"
    }
}