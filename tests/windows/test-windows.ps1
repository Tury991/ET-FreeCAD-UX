#Requires -Version 5.1
# No Pester/download/admin dependency; every write is in a fresh temporary sandbox.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
Import-Module (Join-Path $repo 'tools/windows/ETUX.Windows.psm1') -Force
$suite = Join-Path ([IO.Path]::GetTempPath()) ('ETUX-test-' + [Guid]::NewGuid().ToString('N'))
$fixture = Join-Path $suite ('copia con spazi ' + [char]0x03A9)
$script:count = 0
$script:links = @()

function Assert-True($Value, [string]$Message) {
    if (-not $Value) { throw $Message }
}
function Expect-Failure([scriptblock]$Action) {
    $failed = $false
    try { & $Action | Out-Null } catch { $failed = $true }
    Assert-True $failed 'Operazione non sicura accettata.'
}
function Install-Test([string]$User, [string]$Source = $fixture) {
    & (Join-Path $repo 'install-windows.ps1') -SourceDirectory $Source -FreeCADUserDir $User -Confirm:$false
}
function Uninstall-Test([string]$User) {
    & (Join-Path $repo 'uninstall-windows.ps1') -FreeCADUserDir $User -Confirm:$false
}
function New-TestLink([string]$Path, [string]$Target) {
    $kind = 'SymbolicLink'
    if ($env:OS -eq 'Windows_NT') { $kind = 'Junction' }
    New-Item -ItemType $kind -Path $Path -Target $Target | Out-Null
    $script:links += $Path
}
function Test-Case([string]$Name, [scriptblock]$Action) {
    $caseRoot = Join-Path $suite ([Guid]::NewGuid().ToString('N'))
    $user = Join-Path $caseRoot ('profilo FreeCAD ' + [char]0x00E8)
    [IO.Directory]::CreateDirectory($user) | Out-Null
    try {
        & $Action $user $caseRoot
        $script:count++
        Write-Host ('PASS ' + $Name)
    } finally {
        foreach ($link in $script:links) {
            if (Get-ETUXItem $link) { [IO.Directory]::Delete($link) }
        }
        $script:links = @()
        Assert-ETUXNoReparseTree $caseRoot
        [IO.Directory]::Delete($caseRoot, $true)
    }
}

try {
    [IO.Directory]::CreateDirectory($fixture) | Out-Null
    foreach ($entry in Get-ETUXPayload) {
        Copy-Item -LiteralPath (Join-Path $repo $entry) -Destination $fixture -Recurse -Force
    }
    [IO.Directory]::CreateDirectory((Join-Path $fixture '.git')) | Out-Null
    [IO.Directory]::CreateDirectory((Join-Path $fixture 'work')) | Out-Null
    [IO.File]::WriteAllText((Join-Path $fixture 'freecad-user-path.json'), 'PRIVATE')

    Test-Case '-File senza SourceDirectory: V0.4b, WhatIf e aggiornamento' {
        param($user, $case)
        $engine = (Get-Process -Id $PID).Path
        $installer = Join-Path $fixture 'install-windows.ps1'
        $json = Join-Path $fixture 'freecad-user-path.json'
        @{schema=1; application='FreeCAD'; user_app_data_dir=$user} |
            ConvertTo-Json | Set-Content -LiteralPath $json -Encoding UTF8
        # Seed a complete V0.4b installation, including a file absent in the update.
        Install-Test $user
        $target = Get-ETUXTarget $user
        $marker = Join-Path $target 'etux-package.json'
        @{schema=1; package_id='Tury991/ET-FreeCAD-UX'; version='0.4.0b1'} |
            ConvertTo-Json | Set-Content -LiteralPath $marker -Encoding UTF8
        [IO.File]::WriteAllText((Join-Path $target 'old-only.txt'), 'V04B')
        function Snapshot([string]$Root) {
            @(Get-ChildItem -LiteralPath $Root -Recurse -Force | Sort-Object FullName |
                ForEach-Object {
                    $hash = ''
                    if (-not $_.PSIsContainer) { $hash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash }
                    $_.FullName + '|' + $hash
                }) -join "`n"
        }
        $before = Snapshot $user
        Push-Location $fixture
        try {
            # Same relative -File / JSON arguments as issue #9; no SourceDirectory.
            $output = & $engine -NoProfile -ExecutionPolicy Bypass -File './install-windows.ps1' -UserDataFile './freecad-user-path.json' -WhatIf 2>&1
            Assert-True ($LASTEXITCODE -eq 0) ('WhatIf -File fallito: ' + ($output -join "`n"))
            Assert-True ((Snapshot $user) -eq $before) 'WhatIf ha modificato il profilo o i backup.'
            # Pipe affirmative input so the real high-impact confirmation stays enabled.
            $output = 'Y' | & $engine -NoProfile -ExecutionPolicy Bypass -File './install-windows.ps1' -UserDataFile './freecad-user-path.json' 2>&1
            Assert-True ($LASTEXITCODE -eq 0) ('Upgrade -File fallito: ' + ($output -join "`n"))
        } finally { Pop-Location }
        Assert-ETUXIdentity $target
        Assert-True (-not (Test-Path -LiteralPath (Join-Path $target 'old-only.txt'))) 'Upgrade non eseguito.'
        $backups = @(Get-ChildItem -LiteralPath (Join-Path $user 'ETUX-Backups') -Directory)
        Assert-True ($backups.Count -eq 1) 'Backup V0.4b mancante.'
        Assert-True (([IO.File]::ReadAllText((Join-Path $backups[0].FullName 'old-only.txt'))) -eq 'V04B') 'Backup V0.4b alterato.'
        $old = Get-Content -LiteralPath (Join-Path $backups[0].FullName 'etux-package.json') -Raw | ConvertFrom-Json
        Assert-True ($old.version -eq '0.4.0b1') 'Versione backup errata.'
        # Invocation from another working directory must still use the script copy.
        & $engine -NoProfile -ExecutionPolicy Bypass -File $installer -UserDataFile $json -WhatIf
        Assert-True ($LASTEXITCODE -eq 0) 'Sorgente dipendente dalla directory corrente.'
        Assert-True ((Snapshot $user) -ne $before) 'Upgrade non osservabile.'
        # Fresh profile: the same omitted source also supports first installation.
        $fresh = Join-Path $case 'fresh profile'
        [IO.Directory]::CreateDirectory($fresh) | Out-Null
        $output = 'Y' | & $engine -NoProfile -ExecutionPolicy Bypass -File $installer -FreeCADUserDir $fresh 2>&1
        Assert-True ($LASTEXITCODE -eq 0) ('Prima installazione -File fallita: ' + ($output -join "`n"))
        Assert-ETUXIdentity (Get-ETUXTarget $fresh)
    }
    Test-Case 'installazione locale, spazi/Unicode e altre workbench' {
        param($user, $case)
        $other = Join-Path $user 'Mod/OtherWorkbench'
        [IO.Directory]::CreateDirectory($other) | Out-Null
        [IO.File]::WriteAllText((Join-Path $other 'keep.txt'), 'KEEP')
        Install-Test $user
        $target = Get-ETUXTarget $user
        Assert-ETUXIdentity $target
        Assert-True (Test-Path -LiteralPath (Join-Path $target 'tools/diagnose_freecad.py')) 'Diagnostica non installata.'
        Assert-True (-not (Test-Path -LiteralPath (Join-Path $target '.git'))) 'Copiato .git.'
        Assert-True (-not (Test-Path -LiteralPath (Join-Path $target 'work'))) 'Copiato work.'
        Assert-True (-not (Test-Path -LiteralPath (Join-Path $target 'freecad-user-path.json'))) 'Copiato file privato.'
        Assert-True (([IO.File]::ReadAllText((Join-Path $other 'keep.txt'))) -eq 'KEEP') 'Workbench estranea modificata.'
    }
    Test-Case 'aggiornamento e backup fuori da Mod' {
        param($user, $case)
        Install-Test $user
        $target = Get-ETUXTarget $user
        [IO.File]::WriteAllText((Join-Path $target 'old-only.txt'), 'OLD')
        Install-Test $user
        $backups = @(Get-ChildItem -LiteralPath (Join-Path $user 'ETUX-Backups') -Directory -Filter 'ET-FreeCAD-UX-*')
        Assert-True ($backups.Count -eq 1) 'Backup mancante o duplicato.'
        Assert-True (([IO.File]::ReadAllText((Join-Path $backups[0].FullName 'old-only.txt'))) -eq 'OLD') 'Backup incompleto.'
        Assert-True (-not (Test-Path -LiteralPath (Join-Path $target 'old-only.txt'))) 'Vecchi file mescolati ai nuovi.'
        Assert-True (@(Get-ChildItem -LiteralPath (Join-Path $user 'Mod') -Directory).Count -eq 1) 'Backup caricato come workbench.'
    }
    Test-Case 'aggiornamento legacy senza marker o file Ribbon' {
        param($user, $case)
        Install-Test $user
        $target = Get-ETUXTarget $user
        [IO.File]::Delete((Join-Path $target 'etux-package.json'))
        [IO.File]::Delete((Join-Path $target 'et_freecad_ux/adapters/ribbon.py'))
        [IO.File]::Delete((Join-Path $target 'et_freecad_ux/ui/ribbon.py'))
        # A current catalog without its marker is not a legacy installation.
        # Freeze the real V0.2-V0.4b catalog recognized by the existing guard;
        # expanding commands must not silently rewrite the legacy fixture.
        Copy-Item -LiteralPath (Join-Path $repo 'tests/windows/fixtures/catalog-v02.py.txt') `
            -Destination (Join-Path $target 'et_freecad_ux/core/catalog.py') -Force
        Assert-ETUXIdentity $target
        Install-Test $user
        Assert-ETUXRuntime $target
        Assert-True (Test-Path -LiteralPath (Join-Path $target 'etux-package.json')) 'Marker nuovo mancante.'
    }
    Test-Case 'processo FreeCAD aperto impedisce ogni scrittura' {
        param($user, $case)
        if ($env:OS -ne 'Windows_NT') { return } # Windows-specific process guard.
        function global:Get-Process {
            [CmdletBinding()]
            param([string[]]$Name)
            [pscustomobject]@{ProcessName='FreeCAD'}
        }
        try {
            Expect-Failure { Install-Test $user }
            Expect-Failure { Uninstall-Test $user }
            Assert-True (@(Get-ChildItem -LiteralPath $user -Force).Count -eq 0) 'Profilo modificato con FreeCAD aperto.'
        } finally { Remove-Item Function:\Get-Process }
    }
    Test-Case 'WhatIf installazione senza alcuna scrittura' {
        param($user, $case)
        & (Join-Path $repo 'install-windows.ps1') -SourceDirectory $fixture -FreeCADUserDir $user -WhatIf
        Assert-True (@(Get-ChildItem -LiteralPath $user -Force).Count -eq 0) 'WhatIf ha scritto nel profilo.'
    }
    Test-Case 'sorgente esplicitamente vuota rifiutata senza fallback' {
        param($user, $case)
        Expect-Failure {
            & (Join-Path $repo 'install-windows.ps1') -SourceDirectory '' -FreeCADUserDir $user -Confirm:$false
        }
        Assert-True (@(Get-ChildItem -LiteralPath $user -Force).Count -eq 0) 'Sorgente vuota ha scritto nel profilo.'
    }
    Test-Case 'pacchetto incompleto rifiutato' {
        param($user, $case)
        $broken = Join-Path $case 'broken'
        [IO.Directory]::CreateDirectory($broken) | Out-Null
        Expect-Failure { Install-Test $user $broken }
        Assert-True (-not (Test-Path -LiteralPath (Join-Path $user 'Mod'))) 'Creato Mod prima di verificare la copia.'
    }
    Test-Case 'directory estranea non sovrascritta o rimossa' {
        param($user, $case)
        $target = Get-ETUXTarget $user
        [IO.Directory]::CreateDirectory($target) | Out-Null
        [IO.File]::WriteAllText((Join-Path $target 'keep.txt'), 'KEEP')
        Expect-Failure { Install-Test $user }
        Expect-Failure { Uninstall-Test $user }
        Assert-True (([IO.File]::ReadAllText((Join-Path $target 'keep.txt'))) -eq 'KEEP') 'Directory estranea alterata.'
    }
    Test-Case 'marker estraneo rifiutato' {
        param($user, $case)
        Install-Test $user
        $target = Get-ETUXTarget $user
        [IO.File]::WriteAllText((Join-Path $target 'etux-package.json'), '{"schema":1,"package_id":"Other"}')
        Expect-Failure { Install-Test $user }
        Expect-Failure { Uninstall-Test $user }
        Assert-True (Test-Path -LiteralPath (Join-Path $target 'InitGui.py')) 'Marker estraneo cancellato.'
    }
    Test-Case 'percorso esportato da FreeCAD, non APPDATA hardcoded' {
        param($user, $case)
        $pathFile = Join-Path $case 'profilo.json'
        @{schema=1; application='FreeCAD'; user_app_data_dir=$user} | ConvertTo-Json | Set-Content -LiteralPath $pathFile -Encoding UTF8
        & (Join-Path $repo 'install-windows.ps1') -SourceDirectory $fixture -UserDataFile $pathFile -Confirm:$false
        Assert-ETUXIdentity (Get-ETUXTarget $user)
    }
    Test-Case 'percorso mancante, relativo, radice e JSON malformato rifiutati' {
        param($user, $case)
        Expect-Failure { Get-ETUXUserDirectory '' '' }
        Expect-Failure { Get-ETUXUserDirectory 'relative' '' }
        Expect-Failure { Get-ETUXUserDirectory ([IO.Path]::GetPathRoot($user)) '' }
        $bad = Join-Path $case 'bad.json'
        [IO.File]::WriteAllText($bad, '{bad')
        Expect-Failure { Get-ETUXUserDirectory '' $bad }
        Expect-Failure { Get-ETUXUserDirectory $user $bad }
    }
    Test-Case 'upgrade marker V0.3b senza nuova mappa Ribbon, con backup' {
        param($user, $case)
        Install-Test $user
        $target = Get-ETUXTarget $user
        $marker = Join-Path $target 'etux-package.json'
        @{schema=1; package_id='Tury991/ET-FreeCAD-UX'; version='0.3.0b1'} |
            ConvertTo-Json | Set-Content -LiteralPath $marker -Encoding UTF8
        Remove-Item -LiteralPath (Join-Path $target 'et_freecad_ux/core/ribbon.py')
        Install-Test $user
        Assert-True (Test-Path -LiteralPath (Join-Path $target 'et_freecad_ux/core/ribbon.py')) 'Nuova mappa non installata.'
        $backup = @(Get-ChildItem -LiteralPath (Join-Path $user 'ETUX-Backups') -Directory)[0]
        $old = Get-Content -LiteralPath (Join-Path $backup.FullName 'etux-package.json') -Raw | ConvertFrom-Json
        Assert-True ($old.version -eq '0.3.0b1') 'Backup V0.3b non conservato.'
    }
    Test-Case 'nuova sorgente senza mappa Ribbon rifiutata prima del backup' {
        param($user, $case)
        Install-Test $user
        $incomplete = Join-Path $case 'incomplete'
        Copy-Item -LiteralPath $fixture -Destination $incomplete -Recurse
        Remove-Item -LiteralPath (Join-Path $incomplete 'et_freecad_ux/core/ribbon.py')
        Expect-Failure { Install-Test $user $incomplete }
        Assert-ETUXIdentity (Get-ETUXTarget $user)
        Assert-True (@(Get-ChildItem -LiteralPath (Join-Path $user 'ETUX-Backups') -Directory).Count -eq 0) 'Backup creato per sorgente incompleta.'
    }
    Test-Case 'errore prima della sostituzione conserva versione precedente' {
        param($user, $case)
        Install-Test $user
        $target = Get-ETUXTarget $user
        [IO.File]::WriteAllText((Join-Path $target 'keep-old.txt'), 'OLD')
        [IO.Directory]::Delete((Join-Path $user 'ETUX-Backups'), $true)
        [IO.File]::WriteAllText((Join-Path $user 'ETUX-Backups'), 'BLOCK')
        Expect-Failure { Install-Test $user }
        Assert-True (([IO.File]::ReadAllText((Join-Path $target 'keep-old.txt'))) -eq 'OLD') 'Versione precedente persa.'
    }
    Test-Case 'sorgente annidata nella destinazione rifiutata' {
        param($user, $case)
        Install-Test $user
        Expect-Failure { Install-Test $user (Get-ETUXTarget $user) }
        Assert-ETUXIdentity (Get-ETUXTarget $user)
    }
    Test-Case 'WhatIf disinstallazione e rimozione esclusiva, backup conservato' {
        param($user, $case)
        Install-Test $user
        Install-Test $user
        $other = Join-Path $user 'Mod/OtherWorkbench'
        [IO.Directory]::CreateDirectory($other) | Out-Null
        & (Join-Path $repo 'uninstall-windows.ps1') -FreeCADUserDir $user -WhatIf
        Assert-ETUXIdentity (Get-ETUXTarget $user)
        Uninstall-Test $user
        Assert-True (-not (Test-Path -LiteralPath (Get-ETUXTarget $user))) 'ET UX non rimossa.'
        Assert-True (Test-Path -LiteralPath $other) 'Altra workbench rimossa.'
        Assert-True (@(Get-ChildItem -LiteralPath (Join-Path $user 'ETUX-Backups') -Directory).Count -eq 1) 'Backup rimosso.'
        Uninstall-Test $user  # Idempotent.
    }
    Test-Case 'link del pacchetto rimosso senza toccare destinazione' {
        param($user, $case)
        Install-Test $user
        $target = Get-ETUXTarget $user
        $real = Join-Path $case 'real-package'
        [IO.Directory]::Move($target, $real)
        New-TestLink $target $real
        Expect-Failure { Install-Test $user }
        Uninstall-Test $user
        Assert-ETUXIdentity $real
        Assert-True (-not (Get-ETUXItem $target)) 'Link non rimosso.'
    }
    Test-Case 'Mod tramite junction/link rifiutato' {
        param($user, $case)
        $outside = Join-Path $case 'other-mod'
        [IO.Directory]::CreateDirectory($outside) | Out-Null
        New-TestLink (Join-Path $user 'Mod') $outside
        Expect-Failure { Install-Test $user }
        Expect-Failure { Uninstall-Test $user }
        Assert-True (@(Get-ChildItem -LiteralPath $outside -Force).Count -eq 0) 'Mod esterno modificato.'
    }
    Test-Case 'link interno rifiutato senza attraversare directory estranea' {
        param($user, $case)
        Install-Test $user
        $outside = Join-Path $case 'external'
        [IO.Directory]::CreateDirectory($outside) | Out-Null
        [IO.File]::WriteAllText((Join-Path $outside 'keep.txt'), 'KEEP')
        New-TestLink (Join-Path (Get-ETUXTarget $user) 'linked') $outside
        Expect-Failure { Uninstall-Test $user }
        Expect-Failure { Install-Test $user }
        Assert-True (([IO.File]::ReadAllText((Join-Path $outside 'keep.txt'))) -eq 'KEEP') 'Link interno attraversato.'
    }
    Write-Host ('ETUX_WINDOWS_SCRIPT_TESTS_OK tests=' + $script:count + ' ps=' + $PSVersionTable.PSVersion)
} finally {
    if (Test-Path -LiteralPath $suite) {
        Assert-ETUXNoReparseTree $suite
        [IO.Directory]::Delete($suite, $true)
    }
}
