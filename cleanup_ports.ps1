Write-Host "🧹 Limpando portas 3000, 3001, 8765..."
$ports = 3000, 3001, 8765
foreach ($port in $ports) {
    $pids = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
    if ($pids) {
        foreach ($pid in $pids) {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Write-Host "Porta $port liberada (PID $pid)"
        }
    }
}
Write-Host "✅ Portas limpas!"
