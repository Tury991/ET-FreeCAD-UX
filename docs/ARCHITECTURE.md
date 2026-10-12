# Architettura V0.2 — Mechanical Workspace

ET UX organizza il percorso documento → Body → sketch → feature → modifica usando le azioni native. Il valore aggiunto è l'accesso per attività da una workbench, senza ricreare albero, inspector, solver o task panel. Il [confronto delle estensioni](EXTENSIONS_COMPARISON.md) resta il riferimento per evitare duplicazioni con Nxt/Ribbon.

## Confini

- `core/catalog.py`: dataclass immutabili, quattro gruppi, ID attesi e filtro puro delle capacità. Nessun host, Qt, I/O o stato mutabile globale.
- `adapters/freecad.py`: caricamento esplicito di `PartDesignGui`/`SketcherGui` all'inizializzazione, controllo del registro pubblico `Gui.listCommands()`, diagnosi dei comandi assenti e registrazione idempotente di `ETUX_About` e `ETUX_WorkspaceHelp`.
- `ui/workbench.py`: factory con base Workbench iniettata, `appendToolbar` e `appendMenu`. Toolbar `ET UX Sketch`, `ET UX Features`, `ET UX Reference`, `ET UX Tools`; sottomenu sotto un solo menu `ET UX`.
- `Init.py`: ingresso senza GUI. `InitGui.py`: sola registrazione della classe `ETUXWorkbench`.

## Attivazione e delega

`Initialize` carica i moduli richiesti senza attivare altre workbench, registra i comandi informativi, filtra il catalogo e costruisce la UI una sola volta per istanza. `Activated`/`Deactivated` non installano servizi o modificano preferenze. Nessun timer, observer, connessione Qt o riferimento a documenti richiede cleanup.

I comandi di modellazione sono le **azioni native**, non wrapper Python: FreeCAD valuta il contesto ad ogni aggiornamento, conserva selezioni, Body attivo e transazioni. Non si usa `addObject` nel prodotto. Non si auto-crea un documento/Body e non si forza un Body diverso; con più Body l'utente sceglie nell'albero. Il task sketch può cambiare workbench secondo FreeCAD; ET UX non intercetta né modifica questo comportamento.

Gli ID sono verificati sul runtime effettivo, non dedotti dalla versione. Se un modulo non si carica, gli altri strumenti vengono comunque valutati. Se un ID manca, è omesso da entrambe le superfici e segnalato nel Report. La guida legge nuovamente il registro senza conservare stato. Dopo l'installazione di un modulo mancante è necessario riavviare FreeCAD per ricostruire le toolbar; non si ricostruisce la UI ad ogni attivazione.

Per un comando presente ma non eseguibile, abilitazione e messaggi sono nativi. La guida spiega documento, Body attivo, sketch selezionato, spigoli e task corrente. Non si impone una regola approssimativa duplicata per selezioni valide; non si usano widget privati, monkey patch o API interne. La sola azione Preferenze apre `Std_DlgPreferences` su richiesta dell'utente.

## Verifica

Gli unitari usano fake per registrazione, import, filtro, errori e lifecycle. Le prove geometriche costruiscono Body, sketch vincolato e Pad con le API native in documenti temporanei e controllano ricalcolo/Undo/Redo. Lo smoke GUI controlla il registro reale, menu/toolbar, tre cambi workbench e dispatch di Body/Pad. Le API modello dei test non sono funzionalità ET UX.

Il runner conserva `__main__` di FreeCAD, controlla la versione esatta e propaga i fallimenti. I riferimenti alle QAction dei menu restano vivi durante l'ispezione Qt; la distruzione differita delle viste viene elaborata prima della chiusura del processo di test. Questo codice è solo nel runner/smoke, non nel prodotto.

Risultati e limiti sono in [VALIDATION_V02.md](VALIDATION_V02.md). Loader completo, test manuali Windows/Linux, DPI/temi e disegno interattivo restano gate desktop. Nessuna dipendenza obbligatoria Ribbon/Nxt; nessun codice o asset terzo incorporato. Licenza, metadati Addon Manager, shortcut, traduzioni aggiuntive e Ribbon opzionale sono rinviati.
