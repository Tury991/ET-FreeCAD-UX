#Requires -Version 5.1
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [string]$SourceDirectory,
    [string]$FreeCADUserDir,
    [string]$UserDataFile
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'tools/windows/ETUX.Windows.psm1') -Force

try {
    # Resolve only after script parameter binding, in this script's own scope.
    if (-not $PSBoundParameters.ContainsKey('SourceDirectory')) {
        $SourceDirectory = $PSScriptRoot
    }
    if ([string]::IsNullOrWhiteSpace($SourceDirectory)) {
        throw 'La directory sorgente non puo essere vuota.'
    }
    if (-not $FreeCADUserDir -and -not $UserDataFile) {
        $UserDataFile = Join-Path $PSScriptRoot 'freecad-user-path.json'
    }
    Assert-ETUXClosed
    $userDirectory = Get-ETUXUserDirectory $FreeCADUserDir $UserDataFile
    $target = Get-ETUXTarget $userDirectory
    $source = [IO.Path]::GetFullPath($SourceDirectory)
    Assert-ETUXSource $source $target
    $existing = Get-ETUXItem $target
    if ($existing) {
        Assert-ETUXNoReparseAncestors $target
        Assert-ETUXNoReparseTree $target
        Assert-ETUXIdentity $target
    }
    $operation = 'Installare la copia locale ET-FreeCAD-UX'
    if ($existing) { $operation = 'Aggiornare ET-FreeCAD-UX conservando un backup della versione precedente' }
    Write-Host ('Destinazione: ' + $target)
    if (-not $PSCmdlet.ShouldProcess($target, $operation)) { return }

    $backupRoot = Join-Path $userDirectory 'ETUX-Backups'
    Assert-ETUXNoReparseAncestors $backupRoot
    [IO.Directory]::CreateDirectory($backupRoot) | Out-Null
    $token = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [Guid]::NewGuid().ToString('N')
    $stage = Join-Path $backupRoot ('.etux-stage-' + $token)
    $backup = Join-Path $backupRoot ('ET-FreeCAD-UX-' + $token)
    $movedOld = $false
    $movedNew = $false
    try {
        [IO.Directory]::CreateDirectory($stage) | Out-Null
        foreach ($entry in Get-ETUXPayload) {
            Copy-Item -LiteralPath (Join-Path $source $entry) -Destination $stage -Recurse -Force
        }
        Assert-ETUXNoReparseTree $stage
        Assert-ETUXIdentity $stage
        [IO.Directory]::CreateDirectory((Split-Path -Parent $target)) | Out-Null
        # Recheck after staging, before renaming any existing installation.
        Assert-ETUXNoReparseAncestors $target
        if ($existing) {
            Assert-ETUXNoReparseTree $target
            Assert-ETUXIdentity $target
            [IO.Directory]::Move($target, $backup)
            $movedOld = $true
        } elseif (Get-ETUXItem $target) { throw 'La destinazione e cambiata durante la copia. Riprova.' }
        [IO.Directory]::Move($stage, $target)
        $movedNew = $true
        Assert-ETUXIdentity $target
        Write-Host 'Installazione completata. Riavvia FreeCAD e scegli ET FreeCAD UX.'
        if ($movedOld) { Write-Host ('Backup conservato: ' + $backup) }
    } catch {
        # Preserve failed payloads too; installer never recursively deletes directories.
        if ($movedNew) {
            Assert-ETUXNoReparseAncestors $target
            [IO.Directory]::Move($target, (Join-Path $backupRoot ('failed-' + $token)))
        }
        if ($movedOld) { [IO.Directory]::Move($backup, $target) }
        Write-Warning 'Installazione non completata. La versione precedente e stata conservata; eventuali copie parziali restano in ETUX-Backups.'
        throw
    }
} catch {
    throw ('ET UX: installazione annullata. ' + $_.Exception.Message)
}
