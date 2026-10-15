# Architettura V0.4b — Mechanical Workspace e Ribbon opzionale

La V0.3b mantiene questa architettura runtime e separa deployment/diagnostica
in strumenti locali: [WINDOWS_TECHNICAL.md](WINDOWS_TECHNICAL.md).
Manifest di identita, script PowerShell, macro percorso e diagnostica non
aggiungono dipendenze o preferenze al loader. I comandi e il catalogo restano V0.3a.

ET UX organizza il percorso documento → Body → sketch → feature → modifica usando le azioni native. Il valore aggiunto è l'accesso per attività da una workbench, senza ricreare albero, inspector, solver o task panel. Il [confronto delle estensioni](EXTENSIONS_COMPARISON.md) resta il riferimento per evitare duplicazioni con Nxt/Ribbon.

## Confini

- `core/catalog.py`: dataclass immutabili, quattro gruppi, ID attesi e filtro puro delle capacità. Nessun host, Qt, I/O o stato mutabile globale.
- `adapters/freecad.py`: caricamento esplicito di `PartDesignGui`/`SketcherGui` all'inizializzazione, controllo del registro pubblico `Gui.listCommands()`, diagnosi dei comandi assenti e registrazione idempotente di `ETUX_About` e `ETUX_WorkspaceHelp`.
- `ui/workbench.py`: factory con base Workbench iniettata, `appendToolbar` e `appendMenu`. Toolbar `ET UX Sketch`, `ET UX Features`, `ET UX Reference`, `ET UX Tools`; sottomenu sotto un solo menu `ET UX`.
- `Init.py`: ingresso senza GUI. `InitGui.py`: sola registrazione della classe `ETUXWorkbench`.

## Attivazione e delega

`Initialize` carica i moduli richiesti senza attivare altre workbench, registra i comandi informativi e il toggle Ribbon, filtra il catalogo e costruisce menu/toolbar una sola volta. Il default è standard; la sola densità Ribbon viene letta/scritta nel namespace ET UX su scelta esplicita. `Activated` pianifica la ricreazione Ribbon solo se opt-in, dopo il ripristino toolbar dell'host; `Deactivated` annulla il timer e distrugge il renderer.

`adapters/ribbon.py` risolve le QAction già presenti nelle sole toolbar ET UX, verificando unicità e cardinalità, e implementa `ETUX_ToggleRibbon`. `ui/ribbon.py` crea un QToolBar con QTabWidget, quattro QScrollArea con gruppi etichettati e pulsanti primari/secondari. `setDefaultAction` mantiene identità, stato, testo, icone e dispatch nativi; niente proxy, polling o algoritmi CAD. Il facade PySide viene importato solo all'attivazione.

Il controller possiede widget, timer single-shot e filtro Close della finestra. Snapshot delle dimensioni minime/massime delle toolbar ET UX, compressione a zero senza `hide()` e ripristino idempotente prima di rimuovere il widget. FreeCAD memorizza la visibilità durante i cambi: modificarla con `hide()` ha fallito la prova di ritorno standard ed è stato eliminato. Nessuna toolbar esterna viene modificata. Il filtro Close ripristina prima della chiusura host; se la chiusura viene annullata resta la UI standard fino a nuova attivazione esplicita. Connessioni e figli Qt terminano con `deleteLater`; il runner drena DeferredDelete prima del teardown del runtime.

Il controller non conserva documenti o selezioni. Fallimenti di import Qt, risoluzione o costruzione annullano l'opt-in, ripristinano le dimensioni e lasciano menu/toolbar V0.2 disponibili, con diagnosi Report. Nessuna lettura o scrittura di configurazioni di addon terzi.
`core/ribbon.py` contiene una sola mappa di presentazione e due densità immutabili.
`adapters/ribbon.py` conserva `RibbonDensity` nel solo namespace ET UX e registra
le scelte Classic/Compact. Il renderer cambia metriche senza ricreare azioni o
chiudere task. Il filtro posseduto ascolta anche palette/font/stile della finestra,
applicandoli soltanto ai widget ET UX; lo stylesheet resta locale. Dettagli e
limiti: [RIBBON_V04B.md](RIBBON_V04B.md).

I comandi di modellazione sono le **azioni native**, non wrapper Python: FreeCAD valuta il contesto ad ogni aggiornamento, conserva selezioni, Body attivo e transazioni. Non si usa `addObject` nel prodotto. Non si auto-crea un documento/Body e non si forza un Body diverso; con più Body l'utente sceglie nell'albero. Il task sketch può cambiare workbench secondo FreeCAD; ET UX non intercetta né modifica questo comportamento.

Gli ID sono verificati sul runtime effettivo, non dedotti dalla versione. Se un modulo non si carica, gli altri strumenti vengono comunque valutati. Se un ID manca, è omesso da entrambe le superfici e segnalato nel Report. La guida legge nuovamente il registro senza conservare stato. Dopo l'installazione di un modulo mancante è necessario riavviare FreeCAD per ricostruire le toolbar; non si ricostruisce la UI ad ogni attivazione.

Per un comando presente ma non eseguibile, abilitazione e messaggi sono nativi. La guida spiega documento, Body attivo, sketch selezionato, spigoli e task corrente. Non si impone una regola approssimativa duplicata per selezioni valide; non si usano widget privati, monkey patch o API interne. La sola azione Preferenze apre `Std_DlgPreferences` su richiesta dell'utente.

## Verifica

Gli unitari usano fake per registrazione, import, filtro, errori e lifecycle. Le prove geometriche costruiscono Body, sketch vincolato e Pad con le API native in documenti temporanei e controllano ricalcolo/Undo/Redo. Lo smoke GUI controlla il registro reale, menu/toolbar, tre cambi workbench e dispatch di Body/Pad. Le API modello dei test non sono funzionalità ET UX.

Il runner conserva `__main__` di FreeCAD, controlla la versione esatta e propaga i fallimenti. I riferimenti alle QAction dei menu restano vivi durante l'ispezione Qt; la distruzione differita delle viste viene elaborata prima della chiusura del processo di test. Questo codice è solo nel runner/smoke, non nel prodotto.

Risultati V0.2 e V0.3a: [VALIDATION_V02.md](VALIDATION_V02.md) e [VALIDATION_V03A.md](VALIDATION_V03A.md). Loader completo, test manuali Windows/Linux, DPI/temi e disegno interattivo restano gate desktop. Nessuna dipendenza obbligatoria Ribbon/Nxt; nessun codice o asset terzo incorporato. Licenza, metadati Addon Manager, shortcut e traduzioni aggiuntive sono rinviati.
