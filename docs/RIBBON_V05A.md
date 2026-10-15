# V0.5a — comandi meccanici e Ribbon durante lo sketch

Versione `0.5.0a1`, base V0.4b `ff2217a0e37cac6aa084ddbe6b5fa6033ebf21fe`.
La [matrice preliminare](COMMAND_MATRIX_V05A.md) contiene studio delle alternative,
API verificate, ID nativi, prerequisiti e compatibilità. Le quattro schede restano
**Features, Sketch, Reference, Tools**, identiche in Classic e Compact.

## Utilizzo e comportamento

1. Seleziona ET FreeCAD UX e abilita la Ribbon dal menu ET UX.
2. Crea un Body e uno sketch, oppure seleziona uno sketch esistente e modificalo.
   Il passaggio nativo a Sketcher avviene normalmente. La Ribbon ET UX resta
   disponibile, su una propria riga dopo le toolbar Sketcher, e seleziona Sketch.
   Le toolbar Sketcher restano native e non vengono nascoste da ET UX.
3. Usa geometrie, modifiche, vincoli e quote dalla Ribbon. Abilitazione,
   selezioni, solver, messaggi e pannello Task restano FreeCAD.
4. Chiudi dal comando nativo o dal pulsante Close del task. FreeCAD gestisce
   il ritorno alla workbench precedente; ET UX ripristina la scheda precedente
   (Features se eri su Features). ET UX non forza cambi di workbench.
5. Un cambio volontario di workbench o di documento interrompe la continuità:
   la Ribbon viene rimossa, senza comparire nelle altre workbench. Se torni
   esplicitamente a ET UX, l'opt-in di sessione consente di ricrearla.
6. `Ribbon → Toolbar standard` funziona anche durante lo sketch e rimuove la
   Ribbon senza chiudere il task. Alla chiusura non ricompare. Per riabilitarla
   usa il menu ET UX dopo essere tornato esplicitamente alla workbench.

La continuità riguarda una modifica Sketcher iniziata da ET UX con Ribbon
abilitata. Un passaggio manuale a Sketcher senza modifica attiva non mantiene
la fascia e non prenota una riapparizione per uno sketch aperto successivamente.
Se entri esplicitamente in ET UX con uno sketch già in modifica, il controller
rileva lo stato corrente e seleziona Sketch. Nessuna modifica a `EditingWorkbench`.

## Comandi

**41 azioni native**, più Guida e Informazioni ET UX. Rispetto alla V0.4b sono
aggiunti 17 ID: linea, arco, raccordo sketch, trim, sei vincoli geometrici,
diametro; Hole, Mirrored, Linear/Polar Pattern, Additive/Subtractive Pipe.
Rettangolo, cerchio, distanza, raggio, Pad, Pocket, Revolution, Fillet, Chamfer,
Reference e Tools sono conservati. La [matrice](COMMAND_MATRIX_V05A.md) specifica
tutti gli ID: Mirror usa `PartDesign_Mirrored`, Trim usa `Sketcher_Trimming`.
La registrazione host è controllata prima di costruire entrambe le superfici:
un comando assente viene omesso e segnalato, senza alias o sostituti geometrici.

## Lifecycle e confini

`adapters/sketch.py` possiede un observer GUI, una connessione
`workbenchActivated` e al massimo un timer single-shot. Conserva solo nomi di
documento/oggetto, indice della scheda e stato della transizione; nessun
riferimento persistente a documenti, selezioni o task. Il controller possiede
l'adapter e lo rilascia prima di distruggere i widget, anche su fallback e Close.
`stop` è idempotente, disconnette il segnale, rimuove l'observer e cancella il timer.

Nel runtime reale il segnale `workbenchActivated` precede il vecchio hook
`Deactivated`: il primo identifica ET UX → Sketcher, il secondo mantiene la
verifica differita. Solo `slotInEdit` di uno sketch conferma la continuità;
il callback successivo verifica `getInEdit` e l'identità per nome prima di mostrare
la Ribbon. Una transizione senza editor confermato distrugge la UI temporanea.
Non si usano ritardi euristici, timer ripetuti o polling dei widget task.

La fascia conserva gli stessi pulsanti e QAction durante lo sketch. Il controller
sposta **solo la propria toolbar** dopo quelle ripristinate da Sketcher, inserisce
una separazione di riga e la rimuove nel cleanup. Non modifica dock, menu globali,
dimensioni o visibilità delle toolbar altrui. La compressione delle sole toolbar
ET UX conserva gli snapshot V0.4b ed è ripristinata durante il teardown.

Nessun `Gui.activateWorkbench`, algoritmo geometrico, transazione, preferenza
Sketcher o monkey patch nel nuovo prodotto. La sola preferenza persistente ET UX
resta la densità scelta esplicitamente dall'utente. I task nativi possono salvare
le proprie impostazioni normalmente: ET UX non intercetta tale comportamento.

## Aggiornamento Windows dalla V0.4b

Il branch della PR #10 include ora `main` **a9925e5**, con la correzione installer
della [PR #11](https://github.com/Tury991/ET-FreeCAD-UX/pull/11) per la Issue #9.
Il fix è importato senza modifiche e non cambia le funzionalità V0.5a.
Segui la [guida Windows](WINDOWS_GUIDE.md) usando l'installer della nuova copia:
non occorre specificare `-SourceDirectory`; prova prima con `-WhatIf`.
Rimane disponibile anche questa alternativa manuale:

1. In FreeCAD V0.4b rileva `App.getUserAppDataDir()` dalla console Python.
   Salva i documenti, poi chiudi tutti i processi FreeCAD.
2. Conserva una copia integrale di `<profilo>/Mod/ET-FreeCAD-UX` **fuori da Mod**,
   per esempio in una cartella backup scelta da te. Non sovrapporre i file.
3. Scarica lo ZIP del branch di questa PR, estrailo e colloca la nuova cartella
   completa al posto della precedente. `InitGui.py` deve essere direttamente
   in `<profilo>/Mod/ET-FreeCAD-UX`, senza una seconda cartella annidata.
4. Riavvia FreeCAD 1.1.3, seleziona ET UX e verifica Informazioni: `0.5.0a1`.
   La Ribbon parte spenta; riabilitala esplicitamente. La densità ET UX esistente
   viene letta senza modificare preferenze globali.
5. Per rollback, chiudi FreeCAD, conserva la copia V0.5a fuori da Mod e ripristina
   integralmente la cartella V0.4b dal backup. Evita due copie caricabili in Mod.

Non servono Python, Qt o pip separati. Questo percorso è una procedura manuale
documentata, **non un aggiornamento Windows interattivo già collaudato**.

## Checklist manuale Windows 10/11

Ripetere con Classic e Compact, tema chiaro e scuro, profilo di prova separato:

- [ ] Avvio reale dal loader, versione `0.5.0a1`, nessun errore Report ET UX.
- [ ] Documento → Body → nuovo sketch XY: Ribbon visibile, Sketch selezionata,
  pannello Task e albero funzionanti; nessun cambio forzato o task sostituito.
- [ ] Linea, cerchio, rettangolo, arco; raccordo e trim su geometrie adatte.
- [ ] Orizzontale, verticale, coincidente, tangente, parallelo, perpendicolare;
  distanza/lunghezza, raggio/diametro, selezioni errate e messaggi solver.
- [ ] Chiudi, riapri da albero e da Modifica sketch; comando in corso annullato
  con Escape, poi Close del task. Sketcher non offre un pulsante di rollback
  globale dello sketch: Undo annulla le operazioni, Close termina l'editor.
- [ ] Pad/Pocket/Revolution, Fillet/Chamfer conservati; Hole, Mirrored, serie
  lineare/polare e pipe additive/sottrattive con profili e selezioni validi.
  Conferma e annulla ciascun task nativo; nessuna feature parziale inattesa.
- [ ] Undo/Redo di geometrie, vincoli e feature; ricalcolo, salva/riapri FCStd.
- [ ] Ritorno nativo a ET UX e scheda precedente; cambio volontario a PartDesign
  durante editing, chiusura e nessuna ricomparsa della Ribbon.
- [ ] Passaggio manuale a Sketcher senza editor, poi apertura sketch: nessuna
  riapparizione. Ritorno esplicito a ET UX durante editor aperto.
- [ ] Cambi e chiusure documento con sketch aperto, due documenti e due Body;
  nessun riferimento a documenti chiusi o selezione alterata da ET UX.
- [ ] Cinque toggle, cinque cambi workbench, modifica densità durante task,
  finestra stretta, scroll e tastiera; una sola Ribbon, nessun residuo al termine.
- [ ] DPI 100/125/150/200%, font grandi, più monitor e temi host reali:
  etichette leggibili, stato disabilitato riconoscibile, Task e viewport usabili.
- [ ] Riavvio, aggiornamento dalla V0.4b e rollback; segnalare separatamente #9.

Esiti automatici e limiti: [VALIDATION_V05A](VALIDATION_V05A.md).
