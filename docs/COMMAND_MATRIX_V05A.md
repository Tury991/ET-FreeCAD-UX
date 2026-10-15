# Matrice comandi V0.5a e analisi preliminare

Base: `main` **ff2217a0e37cac6aa084ddbe6b5fa6033ebf21fe** (V0.4b),
verificata il 15 ottobre 2026 via GitHub. Checkout ricostruito dai blob remoti,
con verifica SHA di ogni blob, tree e commit. Nessun aggiornamento installer (#9).

## Architettura e decisione prima dell'implementazione

`core/catalog.py` filtra ID immutabili; `core/ribbon.py` descrive le stesse quattro
schede per Classic e Compact. L'adapter carica PartDesignGui/SketcherGui e verifica
`Gui.listCommands()`. Il renderer risolve le QAction delle toolbar ET UX e usa
`setDefaultAction`: nessuna copia di comando, solver o transazione. Workbench e
controller possiedono attivazione, timer single-shot, filtri e cleanup.
Lo studio [EXTENSIONS_COMPARISON](EXTENSIONS_COMPARISON.md) giustifica l'estensione
circoscritta del renderer esistente: nessun editor Ribbon, tree o inspector nuovo.

Prova esplorativa eseguita sui runtime Linux reali **1.1.3/Qt6** e **1.0.0/Qt5**:
creazione da piano XY, modifica di sketch esistente, chiusura e cambio volontario
a PartDesign. Registro comandi letto dopo i due moduli GUI nativi.

- `ViewProviderSketch::setEdit` attiva Sketcher tramite `Show.TempoVis` prima
  dell'evento GUI `slotInEdit(viewProvider)`; a quel punto il task è già aperto.
- `unsetEdit` chiude il task e ripristina la workbench tramite TempoVis;
  `slotResetEdit` arriva dopo il ripristino. Un cambio volontario a PartDesign
  durante lo sketch viene rispettato anche da TempoVis alla chiusura.
- API verificate: `Gui.addDocumentObserver/removeDocumentObserver`,
  `slotInEdit`, `slotResetEdit`, `slotActivateDocument`, `slotDeletedDocument`,
  `Gui.activeDocument().getInEdit()`, `ViewProvider.Object.isDerivedFrom`,
  `Gui.getMainWindow().workbenchActivated`, Qt `QTimer` single-shot,
  `QToolBar.show`, `QTabWidget.currentIndex/setCurrentIndex` e cleanup QObject.

**A, scelta:** mantenere il widget ET UX esistente solo per la transizione
sincrona ET UX → Sketcher seguita dall'evento InEdit di uno sketch. Un callback
single-shot dopo gli eventi host rende visibile la sola Ribbon ET UX e seleziona
Sketch. Il cambio volontario ad altra workbench o documento interrompe la
sessione e rimuove observer/connessione/widget. Ritorno e task restano nativi.
Nessun polling, nessuna attivazione workbench da ET UX, nessuna modifica preferenze.

**B, scartata:** `ViewObject.EditingWorkbench` è una proprietà nativa dello sketch,
ma modificarla per trattenere ET UX cambierebbe lo stato del documento e il
comportamento scelto dall'utente. Alterare preferenze Sketcher globali o forzare
`Gui.activateWorkbench` durante task sarebbe più invasivo. Nessuna di queste
operazioni è necessaria per A. Se manca una superficie richiesta, fallback standard.

La verifica del registro dimostra presenza, non l'esito geometrico di tutte le
selezioni. Gli strumenti Sketch richiedono modifica sketch attiva; lo stato
effettivo e gli errori restano quelli nativi. La compatibilità sotto riguarda le
build Linux provate, non Windows interattivo. I nomi visualizzati sono descrittivi
italiani: le etichette effettive seguono la traduzione dell'azione FreeCAD.

## Fonti verificabili

- [ViewProviderSketch 1.1.3](https://github.com/FreeCAD/FreeCAD/blob/1.1.3/src/Mod/Sketcher/Gui/ViewProviderSketch.cpp): `setEdit`, `unsetEdit`, `EditingWorkbench`.
- [DocumentObserverPython 1.1.3](https://github.com/FreeCAD/FreeCAD/blob/1.1.3/src/Gui/DocumentObserverPython.cpp): callback GUI e loro argomenti.
- `Show/SceneDetails/Workbench.py` e `Show/mTempoVis.py` del runtime ufficiale:
  ripristino nativo della workbench; codice letto, nessuna modifica o copia.
- Smoke riproducibile V0.5a e risultati: [VALIDATION_V05A](VALIDATION_V05A.md).

## Catalogo

**R/R** = ID presente nei registri reali 1.1.3 e 1.0.0. Le limitazioni specifiche
sono riportate per ogni riga; nessun alias inventato. Le feature richiedono task
sketch concluso per il workflow previsto; FreeCAD può mantenerne l’azione
abilitata anche durante editing. ET UX non sovrascrive questa valutazione nativa. Comandi mancanti in altre build vengono omessi con diagnosi.

| Nome visualizzato | ID nativo | Workbench/modulo | Prerequisiti / limitazioni | In modifica sketch | 1.1.3 / 1.0 |
| --- | --- | --- | --- | --- | --- |
| Nuovo sketch | `PartDesign_NewSketch` | PartDesignGui | Documento, Body/piano o faccia; scelta supporto nel task | Presente; uso dopo Close | R/R |
| Modifica sketch | `Sketcher_EditSketch` | SketcherGui | Sketch selezionato, nessun altro task | Non attivo se già in modifica | R/R |
| Chiudi sketch | `Sketcher_LeaveSketch` | SketcherGui | Sketch in modifica; chiusura nativa | Sì | R/R |
| Linea | `Sketcher_CreateLine` | SketcherGui | Sketch in modifica; Punti iniziale/finale | Sì, secondo selezione | R/R |
| Cerchio | `Sketcher_CreateCircle` | SketcherGui | Sketch in modifica; Centro e raggio | Sì, secondo selezione | R/R |
| Rettangolo | `Sketcher_CreateRectangle` | SketcherGui | Sketch in modifica; Vertici opposti | Sì, secondo selezione | R/R |
| Arco | `Sketcher_CreateArc` | SketcherGui | Sketch in modifica; Centro, estremi | Sì, secondo selezione | R/R |
| Raccordo sketch | `Sketcher_CreateFillet` | SketcherGui | Sketch in modifica; Vertice o geometrie compatibili; può cambiare vincoli | Sì, secondo selezione | R/R |
| Trim | `Sketcher_Trimming` | SketcherGui | Sketch in modifica; Geometria e intersezioni valide; può rimuovere vincoli | Sì, secondo selezione | R/R |
| Orizzontale | `Sketcher_ConstrainHorizontal` | SketcherGui | Sketch in modifica; Linea o punti compatibili | Sì, secondo selezione | R/R |
| Verticale | `Sketcher_ConstrainVertical` | SketcherGui | Sketch in modifica; Linea o punti compatibili | Sì, secondo selezione | R/R |
| Coincidente | `Sketcher_ConstrainCoincident` | SketcherGui | Sketch in modifica; Punti compatibili | Sì, secondo selezione | R/R |
| Tangente | `Sketcher_ConstrainTangent` | SketcherGui | Sketch in modifica; Curve o estremi compatibili | Sì, secondo selezione | R/R |
| Parallelo | `Sketcher_ConstrainParallel` | SketcherGui | Sketch in modifica; Due linee | Sì, secondo selezione | R/R |
| Perpendicolare | `Sketcher_ConstrainPerpendicular` | SketcherGui | Sketch in modifica; Geometrie compatibili | Sì, secondo selezione | R/R |
| Distanza/lunghezza | `Sketcher_ConstrainDistance` | SketcherGui | Sketch in modifica; Linea/punti compatibili; quota nel task nativo | Sì, secondo selezione | R/R |
| Raggio | `Sketcher_ConstrainRadius` | SketcherGui | Sketch in modifica; Cerchio/arco | Sì, secondo selezione | R/R |
| Diametro | `Sketcher_ConstrainDiameter` | SketcherGui | Sketch in modifica; Cerchio/arco | Sì, secondo selezione | R/R |
| Body | `PartDesign_Body` | PartDesignGui | Documento; nessun task; validazione task nativa | Presente; uso dopo Close | R/R |
| Pad | `PartDesign_Pad` | PartDesignGui | Body e profilo chiuso valido; validazione task nativa | Presente; uso dopo Close | R/R |
| Pocket | `PartDesign_Pocket` | PartDesignGui | Solido nel Body e profilo valido; validazione task nativa | Presente; uso dopo Close | R/R |
| Rivoluzione | `PartDesign_Revolution` | PartDesignGui | Body, profilo e asse compatibili; validazione task nativa | Presente; uso dopo Close | R/R |
| Raccordo | `PartDesign_Fillet` | PartDesignGui | Solido, spigoli/facce validi; validazione task nativa | Presente; uso dopo Close | R/R |
| Smusso | `PartDesign_Chamfer` | PartDesignGui | Solido, spigoli/facce validi; validazione task nativa | Presente; uso dopo Close | R/R |
| Foro / Hole | `PartDesign_Hole` | PartDesignGui | Body, solido e sketch/supporto compatibili; validazione task nativa | Presente; uso dopo Close | R/R |
| Specchia / Mirror | `PartDesign_Mirrored` | PartDesignGui | Feature nel Body e piano valido; validazione task nativa | Presente; uso dopo Close | R/R |
| Serie lineare | `PartDesign_LinearPattern` | PartDesignGui | Feature nel Body, direzione e occorrenze; validazione task nativa | Presente; uso dopo Close | R/R |
| Serie polare | `PartDesign_PolarPattern` | PartDesignGui | Feature nel Body, asse e occorrenze; validazione task nativa | Presente; uso dopo Close | R/R |
| Sweep additivo | `PartDesign_AdditivePipe` | PartDesignGui | Body, profilo e percorso compatibili; validazione task nativa | Presente; uso dopo Close | R/R |
| Sweep sottrattivo | `PartDesign_SubtractivePipe` | PartDesignGui | Solido nel Body, profilo e percorso compatibili; validazione task nativa | Presente; uso dopo Close | R/R |
| Piano | `PartDesign_Plane` | PartDesignGui | Body/supporto o riferimenti compatibili; attachment nativo | Presente; uso dopo Close | R/R |
| Linea di riferimento | `PartDesign_Line` | PartDesignGui | Body/supporto o riferimenti compatibili; attachment nativo | Presente; uso dopo Close | R/R |
| Punto | `PartDesign_Point` | PartDesignGui | Body/supporto o riferimenti compatibili; attachment nativo | Presente; uso dopo Close | R/R |
| Sistema di coordinate | `PartDesign_CoordinateSystem` | PartDesignGui | Body/supporto o riferimenti compatibili; attachment nativo | Presente; uso dopo Close | R/R |
| SubShapeBinder | `PartDesign_SubShapeBinder` | PartDesignGui | Body/supporto o riferimenti compatibili; attachment nativo | Presente; uso dopo Close | R/R |
| Nuovo documento | `Std_New` | Gui | Nessuno; cambio documento interrompe la sessione Ribbon | Sì, nativo | R/R |
| Salva | `Std_Save` | Gui | Documento attivo; eventuale dialogo nativo | Secondo stato nativo | R/R |
| Annulla | `Std_Undo` | Gui | Transazione disponibile; stato deciso da FreeCAD | Secondo task nativo | R/R |
| Ripeti | `Std_Redo` | Gui | Transazione disponibile; stato deciso da FreeCAD | Secondo task nativo | R/R |
| Ricalcola | `Std_Refresh` | Gui | Documento attivo; stato deciso da FreeCAD | Secondo task nativo | R/R |
| Preferenze | `Std_DlgPreferences` | Gui | Apertura esplicita; modifiche solo da utente | Sì, nativo | R/R |

Conservati anche `ETUX_WorkspaceHelp` e `ETUX_About`, informativi e read-only,
non comandi nativi. Toggle e densità ET UX restano nel menu Ribbon.
