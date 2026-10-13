"""Metadata contracts plus optional real PowerShell harness, never user profiles."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest
from et_freecad_ux import __version__

ROOT = Path(__file__).resolve().parents[1]


class WindowsPackageTests(unittest.TestCase):
    def test_identity_matches_product_version(self):
        package = json.loads((ROOT / 'etux-package.json').read_text(encoding='utf-8'))
        self.assertEqual(package, {'schema': 1, 'package_id': 'Tury991/ET-FreeCAD-UX',
                                   'version': __version__})

    @unittest.skipUnless(shutil.which('pwsh') or shutil.which('powershell'),
                         'PowerShell unavailable: Windows harness must run on CI/Windows')
    def test_powershell_in_isolated_temporary_profiles(self):
        executable = shutil.which('pwsh') or shutil.which('powershell')
        result = subprocess.run([executable, '-NoProfile', '-NonInteractive', '-File',
                                 str(ROOT / 'tests/windows/test-windows.ps1')],
                                capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('ETUX_WINDOWS_SCRIPT_TESTS_OK', result.stdout)
