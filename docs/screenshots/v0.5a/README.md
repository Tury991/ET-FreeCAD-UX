# Ribbon V0.5a durante editing sketch — catture reali offscreen

FreeCAD 1.1.3 Linux ufficiale, Qt6 6.8.3, DPR 1.0. Quattro catture del widget
Ribbon ET UX con sketch nativo in modifica, task aperto e vincolo orizzontale
applicato dalla Ribbon. Palette chiara/scura sintetiche, non temi host certificati.
Il ritaglio mostra la sola toolbar; non dimostra viewport OpenGL o ergonomia Windows.
Lo scroll orizzontale conserva l'accesso ai comandi fuori dall'area visibile.

| Densità | Chiaro | Scuro |
| --- | --- | --- |
| Classic Modern | [Cattura](sketch-classic-light.png) | [Cattura](sketch-classic-dark.png) |
| Compact Modern | [Cattura](sketch-compact-light.png) | [Cattura](sketch-compact-dark.png) |

Generate da `ETUX_SCREENSHOT_DIR=... bash tools/test_freecad113.sh`, durante
`tools/smoke_sketch_ribbon.py`. [Risultati e limiti](../../VALIDATION_V05A.md).
