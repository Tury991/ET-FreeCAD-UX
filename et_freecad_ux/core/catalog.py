"""Declarative initial UI; future workflow groups belong here, not in Qt widgets."""
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class CommandGroup:
    label: str
    commands: Tuple[str, ...]


ABOUT_COMMAND = "ETUX_About"
GROUPS = (CommandGroup("ET UX", (ABOUT_COMMAND,)),)
