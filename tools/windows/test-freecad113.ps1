#Requires -Version 5.1
# Developer-only runner for an ALREADY extracted official portable runtime.
# No download, pip, second Qt binding, elevated privilege or user-profile writes.
[CmdletBinding()]
param([Parameter(Mandatory = $true)][string]$RuntimeRoot)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$runtime = [IO.Path]::GetFullPath($RuntimeRoot)
$python = @(Get-ChildItem -LiteralPath $runtime -Recurse -File -Filter 'python.exe')
$module = @(Get-ChildItem -LiteralPath $runtime -Recurse -File -Filter 'FreeCAD.pyd')
$ext = @(Get-ChildItem -LiteralPath $runtime -Recurse -Directory -Filter 'Ext')
if ($module.Count -eq 1) {
    # Python ships a second launcher under Lib/venv/scripts/nt; never select it.
    $python = @($python | Where-Object { $_.DirectoryName -eq $module[0].DirectoryName })
}
if ($python.Count -ne 1 -or $module.Count -ne 1 -or $ext.Count -ne 1) {
    Write-Host ('Runtime layout python=' + ($python.FullName -join ',') +
                ' module=' + ($module.FullName -join ',') + ' Ext=' + ($ext.FullName -join ','))
    throw 'Runtime portable ambiguo/incompleto: richiesti un python.exe, FreeCAD.pyd ed Ext.'
}
$profile = Join-Path ([IO.Path]::GetTempPath()) ('ETUX-host-' + [Guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($profile) | Out-Null
$variables = @('FREECAD_USER_HOME', 'FREECAD_USER_DATA', 'FREECAD_USER_TEMP',
               'XDG_CACHE_HOME', 'XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'PATH')
$saved = @{}
foreach ($name in $variables) { $saved[$name] = [Environment]::GetEnvironmentVariable($name, 'Process') }
try {
    foreach ($name in $variables) {
        if ($name -eq 'PATH') { continue }
        $directory = Join-Path $profile $name
        [IO.Directory]::CreateDirectory($directory) | Out-Null
        [Environment]::SetEnvironmentVariable($name, $directory, 'Process')
    }
    $env:PATH = $python[0].DirectoryName + ';' + $module[0].DirectoryName + ';' + $saved['PATH']
    & $python[0].FullName (Join-Path $repo 'tools/check_freecad_runtime.py') `
        --expect-version 1.1.3 --lib-dir $module[0].DirectoryName --ext-dir $ext[0].FullName
    if ($LASTEXITCODE -ne 0) { throw ('Test runtime Windows falliti, exit=' + $LASTEXITCODE) }
} finally {
    foreach ($name in $variables) { [Environment]::SetEnvironmentVariable($name, $saved[$name], 'Process') }
    [IO.Directory]::Delete($profile, $true)
}
