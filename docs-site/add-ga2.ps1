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

$pattern = '<script defer src="/_vercel/insights/script.js"></script>'
$replacement = $pattern + "`n" + $ga

$files = Get-ChildItem *.html
foreach ($f in $files) {
    $content = Get-Content $f -Raw
    if ($content -notmatch 'G-VD5JW3RX34') {
        if ($content.Contains($pattern)) {
            $content = $content.Replace($pattern, $replacement)
            Set-Content $f -Value $content -Encoding UTF8
            Write-Host "Added GA to $($f.Name)"
        } else {
            Write-Host "Pattern not found in $($f.Name)"
        }
    } else {
        Write-Host "GA already in $($f.Name)"
    }
}