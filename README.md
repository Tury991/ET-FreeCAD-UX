# ET-FreeCAD-UX — V0.3b Windows First

Workbench Python per FreeCAD **1.1.3**, con organizzazione originale dei comandi ispirata al workflow dei CAD parametrici professionali. Riusa Part Design e Sketcher; modello, solver, albero delle feature, proprietà, task panel e Undo/Redo restano nativi. Nessun codice o asset proprietario SolidWorks è copiato. Il progetto non è affiliato a SolidWorks o Dassault Systèmes.

La V0.3b conserva V0.1/V0.2/V0.3a e aggiunge installazione locale PowerShell,
aggiornamento con backup, rimozione con conferma e diagnostica da FreeCAD.
**Non servono Python o Qt separati, ambienti di sviluppo o amministratore.**
Segui la [guida Windows 10/11](docs/WINDOWS_GUIDE.md) per installare e collaudare
Body, sketch, Pad e altre feature. [Architettura Windows](docs/WINDOWS_TECHNICAL.md)
e [risultati effettivi](docs/VALIDATION_V03B.md) distinguono CI/offscreen e desktop.

## Comandi

La V0.3a aggiunge un prototipo opzionale scritto per ET UX, senza dipendenze
Ribbon/Nxt: quattro schede **Sketch, Features, Reference e Tools** con le stesse
24 azioni native della V0.2 e i due comandi informativi. Le QAction sono condivise
con le toolbar native: icone, traduzioni, abilitazione e dispatch restano FreeCAD.
Il catalogo V0.2 è invariato. [Studio e scelta](docs/RIBBON_V03A.md).

**Attivazione:** seleziona ET FreeCAD UX e usa `ET UX → Ribbon sperimentale →
Attiva/disattiva Ribbon sperimentale`. **Disattivazione:** stesso comando oppure
`Toolbar standard` nell'angolo della Ribbon. La scelta dura soltanto nella sessione
e parte disattivata al riavvio. Durante il cambio di workbench il prototipo viene
distrutto e ricreato al ritorno; la UI standard è il fallback in caso di errore.
Le sole toolbar ET UX vengono compresse temporaneamente, senza cambiarne la
visibilità memorizzabile; dimensioni, albero, proprietà e task nativi sono preservati.
Due righe di pulsanti, altezza compatta e scorrimento orizzontale nelle schede
per finestre strette. Nessuno stylesheet o asset SolidWorks.

**Verifica:** unitari, geometria e GUI offscreen su 1.1.3/Qt6 e 1.0/Qt5;
risultati e limiti in [VALIDATION_V03A.md](docs/VALIDATION_V03A.md).
Esperienza grafica interattiva, DPI, temi e coesistenza con addon restano da verificare
su desktop. Nessuno screenshot è incluso.

Menu `ET UX` con quattro sottomenu e quattro toolbar native:

| Gruppo | Azioni |
| --- | --- |
| Sketch | Nuovo sketch nel Body, modifica/chiusura sketch, rettangolo, cerchio, distanza, raggio |
| Features | Body, Pad, Pocket, Fillet, Chamfer, Revolution |
| Reference | Piano, linea, punto, sistema di coordinate, SubShapeBinder |
| Tools | Nuovo documento, salva, Undo/Redo, ricalcolo, preferenze native, guida e informazioni |

I pulsanti riusano direttamente gli ID registrati da FreeCAD: icone, traduzioni, abilitazione contestuale, selezione e gestione del Body sono quelle native. Non viene imposto un Body né cambiata automaticamente la workbench. La modifica dello sketch può attivare Sketcher secondo il comportamento nativo; al termine torna a ET FreeCAD UX se necessario.

All'inizializzazione vengono caricati solo `PartDesignGui` e `SketcherGui` e controllato `Gui.listCommands()`. Un comando assente viene omesso con un messaggio nel pannello Report; `Tools → Guida Mechanical Workspace` elenca nuovamente le capacità mancanti e spiega i prerequisiti. Non si inventano alias per versioni non verificate. Errori geometrici e selezioni non valide usano i messaggi e i task nativi di FreeCAD.

Non sono richiesti Ribbon, Nxt, pacchetti pip o un binding Qt esterno. ET UX non scrive preferenze globali; il comando Preferenze apre il dialogo nativo, dove le modifiche restano una scelta esplicita dell'utente.

## Installazione Windows da ZIP locale

1. Scarica/estrai il branch `feature/windows-first-v0.3b`; apri la cartella con
   `InitGui.py` e `install-windows.ps1`.
2. In FreeCAD 1.1.3 apri con File → Apri `tools/export_user_directory.FCMacro`,
   eseguila dall'editor con Macro → Esegui macro/F6 e salva `freecad-user-path.json`
   accanto a `install-windows.ps1`. Il percorso viene rilevato dal FreeCAD effettivo,
   anche per un profilo personalizzato; il JSON è privato.
3. Chiudi tutti i processi FreeCAD. Apri PowerShell **senza amministratore** nella
   cartella estratta ed esegui:

   ```powershell
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\install-windows.ps1" -UserDataFile ".\freecad-user-path.json"
   ```

4. Controlla il percorso mostrato, conferma e riavvia FreeCAD. Scegli **ET FreeCAD UX**.
   Il flag ExecutionPolicy vale solo per quel processo, non modifica la policy globale.

Per aggiornare, ripeti dalla nuova copia estratta e con FreeCAD chiuso. Backup
integrale in `<directory del profilo>/ETUX-Backups`, fuori da Mod; la copia precedente
non viene sovrascritta o mescolata con la nuova. Per disinstallare, dalla copia locale:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\uninstall-windows.ps1" -UserDataFile ".\freecad-user-path.json"
```

La rimozione richiede conferma e riguarda solo ET UX; conserva backup e altre workbench.
Entrambi gli script supportano `-WhatIf`. Non fanno download, non eseguono script
remoti, non scrivono preferenze e gestiscono i percorsi tramite API/literal path.
Non scegliere il profilo presumendo un percorso APPDATA fisso.

## Installazione manuale Linux

1. In FreeCAD apri Visualizza → Pannelli → Console Python ed esegui `print(App.getUserAppDataDir())`. Usa il percorso restituito, poiché varia tra installazioni.
2. Chiudi FreeCAD. Scarica o clona il branch `feature/windows-first-v0.3b` e colloca la directory completa in `<percorso restituito>/Mod/ET-FreeCAD-UX`. `InitGui.py` deve essere direttamente nella root dell'addon, senza una seconda cartella annidata. Preserva eventuali copie precedenti.
3. **Linux:** copia la directory oppure crea un collegamento con `ln -s /percorso/checkout "<directory utente>/Mod/ET-FreeCAD-UX"`, dopo aver creato `Mod`. Non sostituire un collegamento già presente senza controllarlo.
4. Riavvia e seleziona **ET FreeCAD UX** nel selettore delle workbench. Abilita il pannello Report per leggere la guida e le eventuali diagnosi.

Per rimuoverla, chiudi FreeCAD e rimuovi solo la copia o il collegamento dell'addon. Addon Manager, `package.xml` e licenza di distribuzione sono rinviati: l'assenza di `LICENSE` non concede una licenza open source.

## Primo test manuale

1. Seleziona ET FreeCAD UX. In Tools crea un documento; in Features crea un Body. Con più Body, attiva quello desiderato con doppio clic nell'albero.
2. In Sketch crea uno sketch sul piano XY. Disegna un cerchio centrato sull'origine e assegna un vincolo di raggio di **5 mm**. Chiudi lo sketch; torna a ET UX se Sketcher è rimasta attiva.
3. Seleziona lo sketch nell'albero. In Features scegli Pad, imposta **10 mm** e conferma nel task panel nativo. Volume atteso: circa **785,398 mm³**.
4. Riapri lo sketch con Modifica sketch e cambia il raggio a **7 mm**. Chiudi e ricalcola con Tools: volume atteso circa **1539,380 mm³**. Verifica Undo/Redo e modifica anche `Length` del Pad nel pannello proprietà.
5. Seleziona gli spigoli per provare Fillet/Chamfer; crea un secondo sketch su una faccia per Pocket. Per Revolution usa un profilo adatto e scegli l'asse nel task nativo. Conferma o annulla ciascun task prima del successivo.
6. Salva FCStd, chiudi e riapri. Alterna ET UX e Part Design tre volte: devono esserci una sola toolbar per gruppo e un solo menu ET UX. Ripeti anche senza documento e con due Body.

## Test automatici

Dalla root, senza host o dipendenze esterne:

```sh
python3 -m unittest discover -s tests -v
```

Con il runtime ufficiale Linux x86_64 già installato:

```sh
bash tools/install_freecad113.sh
bash tools/test_freecad113.sh
```

Il runner controlla la versione esatta, usa il Python dell'AppImage e un profilo XDG temporaneo con Qt offscreen. `--geometry-only` esegue unitari e geometria senza dichiarare verificata la GUI. Installazione, checksum e comando di regressione 1.0: [guida cloud](docs/FREECAD_113_CLOUD.md).

In una sessione GUI di sviluppo, senza task aperti:

```python
import runpy
runpy.run_path('/percorso/ET-FreeCAD-UX/tools/smoke_freecad.py', run_name='etux_gui_smoke')
```

Lo smoke registra la workbench se necessario e crea/chiude un documento temporaneo: verifica gruppi, disponibilità, assenza di duplicati, comandi Body e Sketch, Body attivo e apertura del task Pad su uno sketch costruito con le API native. Non automatizza il disegno interattivo o l'accettazione dei task. La registrazione rimane nella sessione.

Esiti storici V0.2: [rapporto di verifica](docs/VALIDATION_V02.md). L'offscreen non certifica ergonomia desktop, rendering OpenGL, loader completo dopo riavvio o esperienza interattiva Windows/macOS.

V0.3b: 16 prove script passate su Windows Server 2025 con PowerShell 5.1 e 7;
FreeCAD 1.1.3 Windows reale: 19 unitari, 8 geometrici e GUI/Ribbon/diagnostica
**offscreen** passati. Linux 1.1.3 e 1.0 passano le regressioni (18 unitari passati,
uno skip PowerShell assente, 8 geometrici e GUI/diagnostica). Il desktop Windows
10/11, il loader completo e le macro eseguite dai menu rimangono da collaudare.
Dettagli e CI verificabile in [VALIDATION_V03B.md](docs/VALIDATION_V03B.md).

## Architettura e sviluppo

`core/catalog.py` contiene gruppi immutabili e filtro delle capacità; `adapters/freecad.py` carica i moduli pubblici e registra i comandi informativi; `adapters/ribbon.py` risolve le QAction native e fornisce il toggle ETUX. `ui/workbench.py` costruisce menu e toolbar una sola volta; `ui/ribbon.py` possiede il renderer, un timer di riattivazione cancellabile e il filtro Close, rilasciati su disattivazione. `Init.py` non importa la GUI, `InitGui.py` registra la workbench. Nessun riferimento persistente ai documenti o observer di modello.

Vedi [architettura](docs/ARCHITECTURE.md), [roadmap](docs/ROADMAP.md), [requisiti](docs/REQUIREMENTS.md) e [confronto delle estensioni](docs/EXTENSIONS_COMPARISON.md). Tree e inspector restano nativi; il prototipo non replica editor JSON o servizi globali Ribbon/Nxt.
