# Analisi FreeCAD-Nxt

## Revisione e ambito

Analisi statica del **12 ottobre 2026**, repository [obelisk79/FreeCAD-Nxt](https://github.com/obelisk79/FreeCAD-Nxt), `main`, commit **b0d947d27f32d7e355bbf5736721dd01a2bbece0**, versione dichiarata **0.3.4**. Il README lo indica come sperimentale e in sviluppo intenso. La revisione è stata letta da un clone temporaneo esterno al checkout ET UX; non è stata installata, importata o eseguita come addon.

Non confondere la presenza del sorgente con la compatibilità provata. Nel runtime FreeCAD 1.1.3 sono stati importati solo i moduli QtQuick forniti dall'AppImage, senza caricare Nxt. La sua CI è stata letta, non rieseguita né certificata.

## Architettura osservata

Nxt è un **addon globale**, non una workbench: `package.xml` descrive comandi nel menu Visualizza di tutte le workbench. L'ingresso `freecad/nxt/init_gui.py` registra comandi, un workbench manipulator, preferenze e un avvio differito tramite QTimer. Imposta anche defaults per i gizmo e collega il ripristino all'uscita. Questo lifecycle di sessione è diverso dall'attivazione/disattivazione locale di ET UX.

| Area | Componenti esistenti | Spunto o riuso per ET UX |
| --- | --- | --- |
| `app/` | registro comandi e `Services` di sessione | preferire comandi pubblicati (`Nxt_ModelPanel`, `Nxt_PropertyInspector`, `Nxt_Isolate`) quando disponibili; non importare il singleton servizi |
| `core/` | facade Qt, QtQuick lazy, eventi, transazioni, units, settings | separazione delle capacità e transazioni atomiche; il suo `core` include dipendenze host/Qt, non è interamente Python puro |
| `tree/` | snapshot, modelli/bridge, observer, panel, rollback, link, drag/drop | evitare un secondo tree/FeatureManager ET UX; prima valutare il panel Nxt o quello nativo |
| `inspector/` | proprietà e template TOML, host e bridge | evitare di ricostruire un PropertyManager; mantenere il task panel nativo e valutare inspector opzionale |
| `menus/` | condizioni/fatti, schema TOML, risoluzione, rendering e runner | non creare un secondo motore generico di menu/condizioni per sola estetica; eventuali regole ET UX devono riguardare il percorso guidato |
| `tools/` | isolate, placement, gizmo, floating input, face edit/snap, expression assist, sketch attach/closure/repair, task sync | verificare prima API native e comandi Nxt; riparazioni e modifiche del modello richiedono consenso esplicito, Undo/Redo e test geometrici |
| `ui/` e risorse | QQuickWidget, QML, temi, toast, preferenze e notifiche viewport | ispirazione su separazione view/bridge; nessuna copia di QML, icone o stylesheet in questa modifica |
| `diagnostics/` | probe di capacità e diagnostica geometrica | preferire diagnosi delle capacità concrete invece di dedurre supporto dal solo numero di versione |

`Services.remove()` rimuove event filter, observer e tool e ferma timer. Il codice riconosce dunque ownership e cleanup; resta una superficie ampia e sperimentale da testare prima di considerarla un'integrazione ET UX. Non assumere che chiudere il panel disattivi tutti i servizi: essi hanno durata di sessione.

Il README parla di sostituzione dell'esperienza tree/property. Il codice di `tree/panel.py` costruisce un dock **accanto al tree standard**, con gestione overlay: distinguere intento di prodotto e implementazione effettiva della revisione.

## Qt, Python e FreeCAD

- `package.xml`: FreeCAD minimo **1.1.0**, Python minimo **3.11**.
- `pyproject.toml`: Python >=3.11; TOML letto tramite `tomllib`; strumenti dev includono PySide6 e freecad-stubs.
- `core/qt.py`: facade PySide di FreeCAD, con fallback PySide6 fuori dall'host.
- `core/qtquick.py`: importa **direttamente PySide6.QtQml, QtQuick e QtQuickWidgets**, che non arrivano dal facade PySide di FreeCAD. Il facade QtWidgets da solo non basta: serve una build host Qt6 con moduli compatibili.
- La configurazione della scenegraph è differita alla prima superficie QML; usa OpenGL tramite `QSG_RHI_BACKEND` rispettando un valore già impostato. Questo stato è di processo, non locale alla workbench.

L'AppImage 1.1.3 verificata contiene PySide6/Qt6 6.8.3 e i tre moduli QtQuick importabili. È un **prerequisito soddisfatto**, non una prova che rendering, tree, inspector o gizmo Nxt funzionino in offscreen. L'1.0 Debian disponibile è Qt5/PySide2, senza PySide6: non soddisfa questa implementazione Nxt. Non installare PySide6 da pip dentro quell'host Qt5 per forzare l'integrazione; ET UX deve restare utilizzabile senza Nxt.

## Test e licenza

La revisione include test Python, fake host, verifiche QML e una CI che esegue lint, stile, mypy e ciascun file di test, preservando fallimenti. Usa Python 3.11, Qt offscreen e PySide6 esterno al runtime CAD. La CI fissa `pyside6>=6.8,<6.12`, citando un problema con PySide6 6.12 e Python 3.11. Sono scelte upstream: non dimostrano test geometrici reali su FreeCAD 1.1.3.

`LICENSE` contiene LGPL 2.1; `package.xml` e `pyproject.toml` dichiarano **LGPL-2.1-or-later**. È una dichiarazione più coerente dei metadati Ribbon, ma copiare/adattare moduli o distribuire derivazioni comporta comunque attribuzioni e obblighi, oltre alla verifica delle risorse effettivamente riusate. Nessun codice Nxt è copiato in ET UX; la licenza ET UX resta da decidere.

## Decisione e verifiche future

Nxt copre gran parte delle idee per tree, inspector e interazioni dirette. ET UX deve concentrarsi prima su **guida del workflow PartDesign/Sketcher**, prerequisiti e raggruppamento di comandi nativi, lasciando queste funzionalità a Nxt o FreeCAD quando adeguate.

Un adapter futuro deve rilevare i comandi tramite `Gui.listCommands()` e offrire azioni opzionali solo se disponibili. Anche allora la disponibilità del comando non certifica il comportamento nel contesto. Non fare import privati di `freecad.nxt.app.services`, non manipolare il suo dock o il suo schema TOML in modo non supportato. Le release sperimentali richiedono un pin e una prova prima dell'aggiornamento.

Prima di attivare Nxt con ET UX: profilo di prova separato, selezione/cambio documento, task in modifica, Undo/Redo, interazione dei gizmo e delle riparazioni, rimozione/restart e ripristino preferenze. Testare con Ribbon in una fase distinta, perché entrambi installano servizi/event filter globali. Nessuna combinazione è già certificata.

## Fonti fissate alla revisione

- [README](https://github.com/obelisk79/FreeCAD-Nxt/blob/b0d947d27f32d7e355bbf5736721dd01a2bbece0/README.md), [package.xml](https://github.com/obelisk79/FreeCAD-Nxt/blob/b0d947d27f32d7e355bbf5736721dd01a2bbece0/package.xml), [pyproject.toml](https://github.com/obelisk79/FreeCAD-Nxt/blob/b0d947d27f32d7e355bbf5736721dd01a2bbece0/pyproject.toml), [LICENSE](https://github.com/obelisk79/FreeCAD-Nxt/blob/b0d947d27f32d7e355bbf5736721dd01a2bbece0/LICENSE).
- [init_gui.py](https://github.com/obelisk79/FreeCAD-Nxt/blob/b0d947d27f32d7e355bbf5736721dd01a2bbece0/freecad/nxt/init_gui.py), [services.py](https://github.com/obelisk79/FreeCAD-Nxt/blob/b0d947d27f32d7e355bbf5736721dd01a2bbece0/freecad/nxt/app/services.py), [commands.py](https://github.com/obelisk79/FreeCAD-Nxt/blob/b0d947d27f32d7e355bbf5736721dd01a2bbece0/freecad/nxt/app/commands.py).
- [Qt](https://github.com/obelisk79/FreeCAD-Nxt/blob/b0d947d27f32d7e355bbf5736721dd01a2bbece0/freecad/nxt/core/qt.py), [QtQuick](https://github.com/obelisk79/FreeCAD-Nxt/blob/b0d947d27f32d7e355bbf5736721dd01a2bbece0/freecad/nxt/core/qtquick.py), [panel](https://github.com/obelisk79/FreeCAD-Nxt/blob/b0d947d27f32d7e355bbf5736721dd01a2bbece0/freecad/nxt/tree/panel.py), [menu definitions](https://github.com/obelisk79/FreeCAD-Nxt/blob/b0d947d27f32d7e355bbf5736721dd01a2bbece0/freecad/nxt/menus/definitions.py).
- [test/CI](https://github.com/obelisk79/FreeCAD-Nxt/blob/b0d947d27f32d7e355bbf5736721dd01a2bbece0/.github/workflows/checks.yml).
