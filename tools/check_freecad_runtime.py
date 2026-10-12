"""Run with the selected host's Python. Exact version guard prevents false passes."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback
import unittest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expect-version", required=True)
    parser.add_argument("--lib-dir", required=True)
    parser.add_argument("--ext-dir", required=True)
    parser.add_argument("--geometry-only", action="store_true")
    args = parser.parse_args()
    if sys.flags.optimize:
        raise RuntimeError("Run without -O: the GUI smoke uses assertions.")
    # AppRun forces xcb; override before loading FreeCAD or any Qt module.
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    root = Path(__file__).resolve().parents[1]
    # The native host also parses process arguments during initialization.
    # Do not let it interpret this runner's flags as its own startup options.
    sys.argv = [str(root / "tools" / "check_freecad_runtime.py")]
    sys.path[:0] = [str(root), args.lib_dir, args.ext_dir, str(root / "tools")]
    import FreeCAD as App
    import Part
    actual = ".".join(App.Version()[:3])
    if actual != args.expect_version:
        raise RuntimeError("Expected FreeCAD {}, loaded {}".format(args.expect_version, actual))
    print(json.dumps({"freecad": actual, "python": sys.version.split()[0],
                      "occ": Part.OCC_VERSION}), flush=True)
    suite = unittest.defaultTestLoader.discover(str(root / "tests"))
    unit_count = suite.countTestCases()
    # Keep host mocks in their own process; they must not affect native GUI state.
    unit = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=str(root))
    if unit_count == 0 or unit.returncode != 0:
        return 1
    from smoke_geometry import GeometryTests
    geometry = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(GeometryTests))
    if geometry.testsRun == 0 or not geometry.wasSuccessful():
        return 1
    if not args.geometry_only:
        # Give the native GUI a clean interpreter without runner-specific argv.
        bootstrap = "lib_dir, ext_dir, smoke, expected = {!r}\n".format(
            (args.lib_dir, args.ext_dir, str(root / "tools" / "smoke_freecad.py"),
             args.expect_version)) + '''
import runpy, sys, traceback
sys.path[:0] = [lib_dir, ext_dir]
try:
    import FreeCAD as App
    assert '.'.join(App.Version()[:3]) == expected
    import FreeCADGui as Gui
    # FreeCAD keeps Log/Msg/Err and Workbench in __main__. Preserve it during
    # initialization and command registration; do not run smoke as __main__.
    Gui.showMainWindow()
    runpy.run_path(smoke, run_name='etux_gui_smoke')
    from PySide import QtCore
    print('QT_VERSION=' + QtCore.qVersion(), flush=True)
    try:
        from PySide6 import QtQml, QtQuick, QtQuickWidgets
        print('QTQUICK_MODULES_AVAILABLE=True', flush=True)
    except ImportError:
        print('QTQUICK_MODULES_AVAILABLE=False', flush=True)
    Gui.getMainWindow().close()
except Exception:
    traceback.print_exc(file=sys.__stderr__)
    raise SystemExit(1)
'''
        gui = subprocess.run([sys.executable, "-"], input=bootstrap, text=True, cwd=str(root))
        if gui.returncode != 0:
            return 1
    print("ETUX_RUNTIME_TESTS_OK version={} unit={} geometry={} gui={}".format(
        actual, unit_count, geometry.testsRun, not args.geometry_only), flush=True)
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except Exception:
        # FreeCAD can redirect sys.stderr to its Report pane after GUI startup.
        traceback.print_exc(file=sys.__stderr__)
        code = 1
    raise SystemExit(code)
