# Shared local installer guards. Compatible with Windows PowerShell 5.1.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$script:PackageId = 'Tury991/ET-FreeCAD-UX'
$script:RuntimeFiles = @(
    'Init.py', 'InitGui.py', 'et_freecad_ux/__init__.py',
    'et_freecad_ux/core/__init__.py', 'et_freecad_ux/core/catalog.py',
    'et_freecad_ux/adapters/__init__.py', 'et_freecad_ux/adapters/freecad.py',
    'et_freecad_ux/adapters/ribbon.py', 'et_freecad_ux/ui/__init__.py',
    'et_freecad_ux/ui/workbench.py', 'et_freecad_ux/ui/ribbon.py', 'Resources/icons/etux.svg'
)

function Get-ETUXItem([string]$Path) {
    Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
}

function Assert-ETUXNoReparseAncestors([string]$Path) {
    $current = [IO.Path]::GetFullPath($Path)
    while ($current) {
        $item = Get-ETUXItem $current
        if ($item -and ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw 'Percorso tramite link/junction non consentito. Usa una directory reale.'
        }
        $parent = [IO.Directory]::GetParent($current)
        if (-not $parent) { break }
        $current = $parent.FullName
    }
}

function Assert-ETUXNoReparseTree([string]$Path) {
    $item = Get-ETUXItem $Path
    if (-not $item) { throw 'File o directory richiesti mancanti.' }
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        throw 'Il pacchetto contiene un link/junction: operazione annullata senza seguirlo.'
    }
    if ($item.PSIsContainer) {
        foreach ($child in @(Get-ChildItem -LiteralPath $Path -Force)) {
            Assert-ETUXNoReparseTree $child.FullName
        }
    }
}

function Get-ETUXUserDirectory([string]$FreeCADUserDir, [string]$UserDataFile) {
    if ($FreeCADUserDir -and $UserDataFile) {
        throw 'Specifica solo FreeCADUserDir oppure UserDataFile.'
    }
    if (-not $FreeCADUserDir) {
        if (-not $UserDataFile -or -not (Test-Path -LiteralPath $UserDataFile -PathType Leaf)) {
            throw 'Percorso FreeCAD non rilevato. Esegui tools/export_user_directory.FCMacro in FreeCAD, poi passa -UserDataFile al file JSON salvato; in alternativa usa -FreeCADUserDir con App.getUserAppDataDir().'
        }
        $data = Get-Content -LiteralPath $UserDataFile -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($data.schema -ne 1 -or $data.application -ne 'FreeCAD' -or
            [string]::IsNullOrWhiteSpace($data.user_app_data_dir)) {
            throw 'File percorso non valido: rigeneralo con la macro locale FreeCAD.'
        }
        $FreeCADUserDir = [string]$data.user_app_data_dir
    }
    if (-not [IO.Path]::IsPathRooted($FreeCADUserDir)) { throw 'Il percorso FreeCAD deve essere assoluto.' }
    $full = [IO.Path]::GetFullPath($FreeCADUserDir)
    if ($full.TrimEnd([IO.Path]::DirectorySeparatorChar) -eq
        [IO.Path]::GetPathRoot($full).TrimEnd([IO.Path]::DirectorySeparatorChar)) {
        throw 'La radice di un disco non e una directory utente FreeCAD valida.'
    }
    Assert-ETUXNoReparseAncestors $full
    if (-not (Test-Path -LiteralPath $full -PathType Container)) {
        throw 'La directory utente FreeCAD non esiste. Avvia prima il profilo FreeCAD desiderato.'
    }
    return $full
}

function Assert-ETUXClosed {
    if ($env:OS -eq 'Windows_NT') {
        if (@(Get-Process -Name FreeCAD, FreeCADCmd -ErrorAction SilentlyContinue).Count) {
            throw 'Chiudi tutte le finestre e i processi FreeCAD prima di installare o rimuovere ET UX.'
        }
    }
}

function Assert-ETUXRuntime([string]$Root) {
    foreach ($file in $script:RuntimeFiles) {
        $path = Join-Path $Root $file
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw ('Pacchetto incompleto: manca ' + $file)
        }
    }
}

function Get-ETUXNormalizedHash([string]$Path) {
    # Git checkouts on Windows may use CRLF; ZIP copies usually use LF.
    $text = [IO.File]::ReadAllText($Path, [Text.Encoding]::UTF8).Replace("`r`n", "`n")
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($algorithm.ComputeHash([Text.Encoding]::UTF8.GetBytes($text)))).Replace('-', '')
    } finally { $algorithm.Dispose() }
}

function Assert-ETUXIdentity([string]$Root) {
    $marker = Join-Path $Root 'etux-package.json'
    if (Test-Path -LiteralPath $marker -PathType Leaf) {
        Assert-ETUXRuntime $Root
        $data = Get-Content -LiteralPath $marker -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($data.schema -ne 1 -or $data.package_id -ne $script:PackageId) {
            throw 'Identita del pacchetto non valida: nessuna modifica eseguita.'
        }
    } else {
        # Legacy V0.1/V0.2/V0.3a: fixed loader/catalog hashes, not folder name alone.
        foreach ($file in $script:RuntimeFiles) {
            if ($file -in @('et_freecad_ux/adapters/ribbon.py', 'et_freecad_ux/ui/ribbon.py')) { continue }
            if (-not (Test-Path -LiteralPath (Join-Path $Root $file) -PathType Leaf)) {
                throw ('Installazione legacy incompleta: manca ' + $file)
            }
        }
        $loader = Get-ETUXNormalizedHash (Join-Path $Root 'InitGui.py')
        $catalog = Get-ETUXNormalizedHash (Join-Path $Root 'et_freecad_ux/core/catalog.py')
        if ($loader -ne 'CF45807F452296AFB3185FB4072D21469D7A1040E041948DAEE936EBCAC1C3CE' -or
            $catalog -notin @('B68D36663554A7150BEE2B670E59966702FCE965AB7D3E043396533BFD6D31E0',
                             '0383F8C087F2967B470F52ABB6B0A8AF64D9D6F67BAA1F1E77FDB10C8889862F')) {
            throw 'Directory estranea o versione legacy non riconosciuta: nessuna modifica eseguita.'
        }
    }
}

function Get-ETUXTarget([string]$UserDirectory) {
    $mod = Join-Path $UserDirectory 'Mod'
    Assert-ETUXNoReparseAncestors $mod
    $item = Get-ETUXItem $mod
    if ($item -and -not $item.PSIsContainer) { throw 'Mod esiste ma non e una directory.' }
    return (Join-Path $mod 'ET-FreeCAD-UX')
}

function Get-ETUXPayload {
    @('Init.py', 'InitGui.py', 'etux-package.json', 'README.md',
      'install-windows.ps1', 'uninstall-windows.ps1',
      'et_freecad_ux', 'Resources', 'docs', 'tools')
}

function Assert-ETUXSource([string]$Root, [string]$Target) {
    Assert-ETUXNoReparseAncestors $Root
    Assert-ETUXIdentity $Root
    foreach ($file in @('etux-package.json', 'install-windows.ps1', 'uninstall-windows.ps1',
                       'tools/windows/ETUX.Windows.psm1', 'tools/diagnose_freecad.py',
                       'tools/export_user_directory.FCMacro', 'docs/WINDOWS_GUIDE.md')) {
        if (-not (Test-Path -LiteralPath (Join-Path $Root $file) -PathType Leaf)) {
            throw ('Copia V0.3b incompleta: manca ' + $file)
        }
    }
    $separator = [IO.Path]::DirectorySeparatorChar
    $a = $Root.TrimEnd($separator) + $separator
    $b = $Target.TrimEnd($separator) + $separator
    if ($a.StartsWith($b, [StringComparison]::OrdinalIgnoreCase) -or
        $b.StartsWith($a, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Sorgente e destinazione devono essere directory separate e non annidate.'
    }
    foreach ($entry in Get-ETUXPayload) { Assert-ETUXNoReparseTree (Join-Path $Root $entry) }
}

Export-ModuleMember -Function *-ETUX*
