"""Immutable mechanical workspace; command IDs are validated by the adapter."""
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class CommandGroup:
    label: str
    commands: Tuple[str, ...]


ABOUT_COMMAND = 'ETUX_About'
HELP_COMMAND = 'ETUX_WorkspaceHelp'
GROUPS = (
    CommandGroup('Sketch', ('PartDesign_NewSketch', 'Sketcher_EditSketch',
        'Sketcher_LeaveSketch', 'Sketcher_CreateRectangle', 'Sketcher_CreateCircle',
        'Sketcher_CreateLine', 'Sketcher_CreateArc', 'Sketcher_CreateFillet',
        'Sketcher_Trimming', 'Sketcher_ConstrainHorizontal', 'Sketcher_ConstrainVertical',
        'Sketcher_ConstrainCoincident', 'Sketcher_ConstrainTangent',
        'Sketcher_ConstrainParallel', 'Sketcher_ConstrainPerpendicular',
        'Sketcher_ConstrainDistance', 'Sketcher_ConstrainRadius', 'Sketcher_ConstrainDiameter')),
    CommandGroup('Features', ('PartDesign_Body', 'PartDesign_Pad', 'PartDesign_Pocket',
        'PartDesign_Fillet', 'PartDesign_Chamfer', 'PartDesign_Revolution',
        'PartDesign_Hole', 'PartDesign_Mirrored', 'PartDesign_LinearPattern',
        'PartDesign_PolarPattern', 'PartDesign_AdditivePipe', 'PartDesign_SubtractivePipe')),
    CommandGroup('Reference', ('PartDesign_Plane', 'PartDesign_Line',
        'PartDesign_Point', 'PartDesign_CoordinateSystem', 'PartDesign_SubShapeBinder')),
    CommandGroup('Tools', ('Std_New', 'Std_Save', 'Std_Undo', 'Std_Redo',
        'Std_Refresh', 'Std_DlgPreferences', HELP_COMMAND, ABOUT_COMMAND)),
)
NATIVE_COMMANDS = tuple(c for g in GROUPS for c in g.commands if not c.startswith('ETUX_'))


def available_groups(available):
    """Filter unsupported commands without guessing aliases or changing order."""
    return tuple(CommandGroup(g.label, tuple(c for c in g.commands if c in available))
                 for g in GROUPS)
