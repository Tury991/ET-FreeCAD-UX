"""Session-only diagnostics in FreeCAD's Python; returns an allowlisted report.

No documents, paths, user names, model names, exception text or Report history
are exported. Missing registration is reported, never masked by manual loading.
"""
import json
import platform
from pathlib import Path
import sys


def _sizes(bar):
    minimum, maximum = bar.minimumSize(), bar.maximumSize()
    return (minimum.width(), minimum.height(), maximum.width(), maximum.height(),
            bar.isHidden())


def run(app=None, gui=None, qt=None):
    if app is None:
        import FreeCAD as app
    if gui is None:
        import FreeCADGui as gui
    if qt is None:
        from PySide import QtCore, QtWidgets
    else:
        QtCore, QtWidgets = qt
    # Allow execution from a downloaded copy even if the addon failed to load.
    root = str(Path(__file__).resolve().parents[1])
    inserted = root not in sys.path
    if inserted:
        sys.path.insert(0, root)
    try:
        from et_freecad_ux import __version__
        from et_freecad_ux.core.catalog import GROUPS, NATIVE_COMMANDS
        from et_freecad_ux.core.ribbon import SECTIONS
    finally:
        if inserted:
            sys.path.remove(root)
    version = '.'.join(app.Version()[:3])
    report = {'schema': 1, 'tool': 'ETUX_WindowsFirst', 'etux_version': __version__,
              'environment': {'system': platform.system(), 'python': platform.python_version(),
                              'freecad': version, 'qt': QtCore.qVersion(),
                              'binding': QtCore.QObject.__module__.split('.')[0]},
              'checks': {}, 'errors': []}
    checks = report['checks']
    checks['reference_113'] = version == '1.1.3'
    checks['supported_version'] = version in ('1.1.3', '1.0.0')
    checks['registered'] = 'ETUXWorkbench' in gui.listWorkbenches()
    if not checks['registered']:
        report['errors'].append({'phase': 'registration', 'code': 'workbench_not_loaded'})
        report['status'] = 'fail'
        return report
    if gui.Control.activeDialog():
        report['errors'].append({'phase': 'preflight', 'code': 'finish_or_cancel_native_task'})
        report['status'] = 'blocked'
        return report

    previous = gui.activeWorkbench().name()
    wb = gui.getWorkbench('ETUXWorkbench')
    previous_enabled = getattr(wb, '_etux_ribbon_enabled', False)
    try:
        gui.activateWorkbench('ETUXWorkbench')
        gui.updateGui()
        wb.setRibbonEnabled(False)
        QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
        window = gui.getMainWindow()
        missing = [c for c in NATIVE_COMMANDS if c not in gui.listCommands()]
        report['missing_commands'] = missing
        checks['native_commands'] = not missing
        bars = [window.findChildren(QtWidgets.QToolBar, 'ET UX ' + g.label) for g in GROUPS]
        report['toolbar_counts'] = {g.label: len(found) for g, found in zip(GROUPS, bars)}
        checks['unique_toolbars'] = all(len(found) == 1 for found in bars)
        if not checks['unique_toolbars']:
            raise RuntimeError('nonunique_toolbar')
        bars = [found[0] for found in bars]
        baseline = [_sizes(b) for b in bars]
        docks = set(window.findChildren(QtWidgets.QDockWidget))
        for _ in range(2):
            wb.setRibbonEnabled(True)
            gui.updateGui()
            ribbons = window.findChildren(QtWidgets.QToolBar, 'ETUX_RibbonPrototype')
            checks['unique_ribbon'] = len(ribbons) == 1
            if not checks['unique_ribbon']:
                raise RuntimeError('ribbon_not_created')
            tabs = ribbons[0].findChild(QtWidgets.QTabWidget, 'ETUX_RibbonTabs')
            labels = [tabs.tabText(i) for i in range(tabs.count())] if tabs else []
            report['ribbon_tabs'] = [label if label in ('Sketch', 'Features', 'Reference', 'Tools')
                                     else 'unexpected_label' for label in labels]
            checks['four_tabs'] = labels == [label for label, _ in SECTIONS]
            wb.setRibbonEnabled(False)
            QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
            checks['ribbon_removed'] = not window.findChildren(QtWidgets.QToolBar, 'ETUX_RibbonPrototype')
            checks['standard_restored'] = baseline == [_sizes(b) for b in bars]
            if not all(checks[k] for k in ('four_tabs', 'ribbon_removed', 'standard_restored')):
                raise RuntimeError('ribbon_lifecycle_failed')
        alternative = 'PartDesignWorkbench' if 'PartDesignWorkbench' in gui.listWorkbenches() else previous
        if alternative != 'ETUXWorkbench':
            wb.setRibbonEnabled(True)
            gui.activateWorkbench(alternative)
            gui.updateGui()
            gui.activateWorkbench('ETUXWorkbench')
            gui.updateGui()
            checks['workbench_switch'] = len(window.findChildren(QtWidgets.QToolBar, 'ETUX_RibbonPrototype')) == 1
            wb.setRibbonEnabled(False)
            checks['switch_restored'] = baseline == [_sizes(b) for b in bars]
        else:
            report['errors'].append({'phase': 'switch', 'code': 'alternative_workbench_not_registered'})
            checks['workbench_switch'] = False
        checks['native_docks_preserved'] = docks == set(window.findChildren(QtWidgets.QDockWidget))
    except Exception as error:
        # Intentionally omit message/traceback: they can contain private paths.
        report['errors'].append({'phase': 'gui_checks', 'code': 'check_failed',
                                 'error_type': type(error).__name__})
    finally:
        try:
            wb.setRibbonEnabled(False)
            gui.activateWorkbench(previous)
            gui.updateGui()
            if previous == 'ETUXWorkbench':
                wb.setRibbonEnabled(previous_enabled)
            else:
                wb._etux_ribbon_enabled = previous_enabled  # Own session flag; no host preference.
            QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
            checks['session_restored'] = (gui.activeWorkbench().name() == previous and
                                         wb._etux_ribbon_enabled == previous_enabled)
        except Exception as error:
            report['errors'].append({'phase': 'restore', 'code': 'restore_failed',
                                     'error_type': type(error).__name__})
            checks['session_restored'] = False
    checks['no_diagnostic_failures'] = not report['errors']
    report['status'] = 'pass' if all(value for key, value in checks.items()
                                   if key != 'reference_113') and not report['errors'] else 'fail'
    return report


def save_report(report, filename):
    """Explicit user-selected output; never add machine state to the report."""
    Path(filename).write_text(json.dumps(report, ensure_ascii=True, indent=2), encoding='utf-8')
