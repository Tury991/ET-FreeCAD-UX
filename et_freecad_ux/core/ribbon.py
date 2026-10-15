"""One immutable presentation map for both densities; no host dependencies."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Density:
    key: str
    label: str
    primary_icon: int
    secondary_icon: int
    spacing: int
    padding: int
    command_height: int


DENSITIES = (
    Density('classic', 'Classic Modern', 40, 24, 10, 8, 152),
    Density('compact', 'Compact Modern', 32, 20, 4, 4, 96),
)


def density(key):
    return next((item for item in DENSITIES if item.key == key), DENSITIES[0])


# Explicit IDs from the verified catalog only. Tuple order is visual/tab order.
SECTIONS = (
    ('Features', (
        ('Struttura', ('PartDesign_Body',), True),
        ('Volume', ('PartDesign_Pad', 'PartDesign_Pocket', 'PartDesign_Revolution'), True),
        ('Finitura', ('PartDesign_Fillet', 'PartDesign_Chamfer'), False))),
    ('Sketch', (
        ('Sessione', ('PartDesign_NewSketch', 'Sketcher_EditSketch', 'Sketcher_LeaveSketch'), True),
        ('Geometria', ('Sketcher_CreateRectangle', 'Sketcher_CreateCircle'), True),
        ('Quote e vincoli', ('Sketcher_ConstrainDistance', 'Sketcher_ConstrainRadius'), False))),
    ('Reference', (
        ('Riferimenti', ('PartDesign_Plane', 'PartDesign_Line', 'PartDesign_Point',
                         'PartDesign_CoordinateSystem', 'PartDesign_SubShapeBinder'), True),)),
    ('Tools', (
        ('Documento', ('Std_New', 'Std_Save'), True),
        ('Cronologia', ('Std_Undo', 'Std_Redo'), False),
        ('Strumenti', ('Std_Refresh', 'Std_DlgPreferences'), False),
        ('Supporto', ('ETUX_WorkspaceHelp', 'ETUX_About'), False))),
)


def ribbon_sections(actions):
    """Keep capability omissions without introducing replacement actions."""
    return tuple((tab, tuple((label, tuple((c, actions[c]) for c in commands if c in actions), primary)
                            for label, commands, primary in sections))
                 for tab, sections in SECTIONS)
