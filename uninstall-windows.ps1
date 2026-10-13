#Requires -Version 5.1
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param([string]$FreeCADUserDir, [string]$UserDataFile)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'tools/windows/ETUX.Windows.psm1') -Force

try {
    if (-not $FreeCADUserDir -and -not $UserDataFile) {
        $UserDataFile = Join-Path $PSScriptRoot 'freecad-user-path.json'
    }
    Assert-ETUXClosed
    $userDirectory = Get-ETUXUserDirectory $FreeCADUserDir $UserDataFile
    $target = Get-ETUXTarget $userDirectory
    $item = Get-ETUXItem $target
    if (-not $item) { Write-Host 'ET-FreeCAD-UX non installata in questo profilo. Nessuna modifica.'; return }
    if (-not $item.PSIsContainer) { throw 'La destinazione non e una directory ET UX.' }
    $isLink = [bool]($item.Attributes -band [IO.FileAttributes]::ReparsePoint)
    if (-not $isLink) { Assert-ETUXNoReparseTree $target }
    # Read-only identity check. Dangling/foreign links fail before deletion.
    Assert-ETUXIdentity $target
    $operation = 'Rimuovere esclusivamente ET-FreeCAD-UX (i backup saranno conservati)'
    if ($isLink) { $operation = 'Rimuovere soltanto il link ET-FreeCAD-UX, conservando la sua destinazione' }
    Write-Host ('Destinazione: ' + $target)
    if (-not $PSCmdlet.ShouldProcess($target, $operation)) { return }
    $now = Get-ETUXItem $target
    if (-not $now -or [bool]($now.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne $isLink) {
        throw 'La destinazione e cambiata. Nessuna cancellazione eseguita.'
    }
    Assert-ETUXIdentity $target
    if ($isLink) {
        [IO.Directory]::Delete($target)  # Non-recursive: removes the link, never its target.
    } else {
        Assert-ETUXNoReparseAncestors $target
        Assert-ETUXNoReparseTree $target
        [IO.Directory]::Delete($target, $true)
    }
    Write-Host 'ET-FreeCAD-UX rimossa. Backup e altre workbench conservati. Riavvia FreeCAD.'
} catch {
    throw ('ET UX: disinstallazione annullata. ' + $_.Exception.Message)
}
