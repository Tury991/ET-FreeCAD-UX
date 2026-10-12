# FreeCAD 1.1.3 nel cloud: installazione e prove

## Aggiornamento V0.2

Il 12 ottobre 2026 (Europe/Rome), la suite Mechanical Workspace ha superato **8 unitari, 8 geometrici e smoke GUI** sia su 1.1.3 sia su 1.0.0. Dettagli attuali: [VALIDATION_V02.md](VALIDATION_V02.md). I conteggi 4/4 e lo stato V0.1 nelle sezioni successive documentano la verifica precedente.

Il runner aggiunge al percorso Python `App.getResourceDir()/Mod` del solo runtime selezionato e, nel bootstrap GUI minimale, registra i loader ufficiali PartDesign/Sketcher se assenti. Questo consente ai task nativi di attivare le rispettive workbench su Debian 1.0. Il namespace `__main__`, la versione esatta e gli exit code restano preservati.

## Provenienza e installazione

Verifica effettuata il **12 ottobre 2026**, Linux x86_64, ambiente cloud Debian. La [release ufficiale 1.1.3](https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.3) contiene l'AppImage `FreeCAD_1.1.3-Linux-x86_64-py311.AppImage`. Il tag Git punta a `145529fe741292ff0b3977a01195bf0247425794`, corrispondente alla versione mostrata dal runtime. È presente anche il tag 1.1.4: non è stato sostituito al riferimento richiesto.

SHA256 dell'AppImage, verificato sia sul file `-SHA256.txt` ufficiale sia sul digest mostrato nella pagina degli asset:

```text
3a853eb69ee595f779f2255dbf80a765926981d8ff68903cefee4dfb03a8f5ef
```

Dalla root del checkout:

```sh
bash tools/install_freecad113.sh
bash tools/test_freecad113.sh
```

Lo script scarica via HTTPS verificato, controlla il digest **prima di eseguire l'artefatto** e usa `--appimage-extract`; non occorre FUSE. La cache e l'estrazione risiedono in `/workspace/.local/freecad/1.1.3`, fuori dal repository, senza modificare pacchetti apt, `/usr/bin` o Python di sistema. Il download è circa 782 MiB e l'estrazione circa 3.1 GiB. Non serve compilare FreeCAD. In caso di estrazione interrotta lo script usa uno staging temporaneo e non adotta directory di provenienza sconosciuta.

L'installazione manuale iniziale è stata estratta dall'artefatto verificato e marcata come tale. Il comando riutilizzabile è stato poi eseguito sul runtime preparato; un'ulteriore esecuzione ha verificato la cache senza reinstallare. È stato inoltre provato da zero in una directory temporanea, includendo download, checksum, estrazione e avvio del Python 3.11.14 incluso; il runtime di prova è stato rimosso. Il marker di estrazione identifica l'origine per il riuso, non controlla ogni file estratto: dopo modifiche locali al runtime occorre ripreparare l'estrazione da un artefatto verificato.

L'override `ETUX_FREECAD_INSTALL_DIR` deve indicare un percorso assoluto dedicato fuori dal checkout. Lo script iniziale supporta solo Linux x86_64; le release arm64/Windows/macOS esistono, ma non sono state testate qui.

## Avvio e isolamento

Il launcher dell'AppImage imposta `PYTHONHOME` al runtime incluso e forza `QT_QPA_PLATFORM=xcb`. Il runner usa il launcher con l'interprete `python` incluso e reimposta **offscreen prima di importare Qt**. Aggiunge solo i percorsi `usr/lib` e `usr/Ext` dello stesso runtime: non mescola i moduli FreeCAD/Qt del sistema con quelli AppImage.

`test_freecad113.sh` crea un profilo XDG temporaneo per cache, configurazione e dati, rimosso al termine. Mantiene separati test unitari con mock, geometria e GUI attraverso processi dedicati. Il controllo della versione è esatto: una build 1.0.0 non può essere registrata come esito positivo 1.1.3. Il runner propaga un exit code diverso da zero per suite fallita, vuota o smoke fallito. È stato verificato anche il failure path: il runtime 1.0.0 richiesto come 1.1.3 termina con exit code 1 e diagnosi esplicita prima di eseguire test. Eseguirlo senza `-O`, perché lo smoke GUI usa assert.

La modalità `bash tools/test_freecad113.sh --geometry-only` esegue unitari e geometria senza GUI. Non dichiara verificata la GUI e produce `gui=False`.

## Esiti osservati

| Runtime | Test unitari originali | Test geometrici nuovi | GUI offscreen ET UX | QtQuick |
| --- | --- | --- | --- | --- |
| 1.1.3 / Python 3.11.14 / Qt6 6.8.3 / OCC 7.8.1 | 4 passati | 4 passati | passato, tre attivazioni | QtQml/QtQuick/QtQuickWidgets importabili |
| 1.0.0 Debian / Python 3.13.5 / Qt5 5.15.15 / OCC 7.8.1 | 4 passati | 4 passati | passato, tre attivazioni | PySide6 non presente |

Le prove geometriche verificano volume/validità di un Box, volume/validità di una differenza booleana, modifica parametrica con Undo/Redo e salvataggio/riapertura FCStd. Creano e chiudono solo documenti temporanei. Sono verifiche dell'host: non introducono algoritmi geometrici ET UX e non modificano il kernel.

Lo smoke GUI verifica registrazione della workbench, esistenza di menu/toolbar, comando informativo e tre cicli senza toolbar duplicate. Le uscite positive comprendono:

```text
ETUX_GUI_SMOKE_OK
ETUX_RUNTIME_TESTS_OK version=1.1.3 unit=4 geometry=4 gui=True
```

Il README riporta anche il comando specifico per verificare l'1.0 Debian. La workbench di prodotto conserva la versione 0.1.0: qui si aggiorna strategia e infrastruttura, non si implementa la V0.2.

## Problemi incontrati e correzioni

- **Cache utente non scrivibile:** il primo import 1.1.3 abortiva tentando `/home/agent/.cache/FreeCAD/v1-1`. Risolto usando le directory XDG temporanee scrivibili; non è stato necessario cambiare HOME.
- **Launcher xcb:** l'AppRun ufficiale sovrascrive l'impostazione offscreen esterna. Risolto nel bootstrap Python prima degli import Qt, senza modificare AppRun.
- **Namespace di avvio:** FreeCAD conserva `Log`, `Msg`, `Err` e la classe `Workbench` in `__main__`. Importare App nel bootstrap e poi eseguire lo smoke come `__main__` sostituiva quel namespace, causando `NameError: Log`, `Cannot create main window` o un crash nativo durante la registrazione. Il runner inizializza la GUI nel suo namespace e usa `run_name='etux_gui_smoke'`, mantenendo `__main__`. La sequenza corretta supera lo smoke. Questo è un problema del runner di test, non una modifica al motore o una prova di incompatibilità della workbench.
- **Avvisi Qt offscreen:** compaiono avvisi `propagateSizeHints` e `QThreadStorage` alla chiusura; le verifiche funzionali e l'exit code passano. Non implicano una prova del viewport OpenGL o dei widget QML Nxt.
- **GUI minimale 1.0:** può comparire `Unknown command Std_AddonMgr`, perché Addon Manager non è caricato in questa modalità; lo smoke non lo richiede e passa.
- **`freecadcmd` 1.0 di sistema:** il segfault nativo dell'onboarding resta separato. Per regressione 1.0 si usa `/usr/bin/python3` con i moduli del sistema; non si afferma di aver riparato quel binario.
- **API GitHub:** inizialmente il proxy negava `api.github.com`, mentre download ufficiale via github.com e Git HTTPS funzionavano. Dopo i successivi aggiornamenti della configurazione, una lettura autenticata del repository tramite API è riuscita. La disponibilità è stata verificata con la richiesta reale; la sola presenza del dominio in bozza non avrebbe dimostrato accesso runtime.

Riferimenti sul namespace: [FreeCADGuiInit.py](https://github.com/FreeCAD/FreeCAD/blob/145529fe741292ff0b3977a01195bf0247425794/src/Gui/FreeCADGuiInit.py), [ApplicationPy.cpp](https://github.com/FreeCAD/FreeCAD/blob/145529fe741292ff0b3977a01195bf0247425794/src/Gui/ApplicationPy.cpp) e [FreeCADGuiPy.cpp](https://github.com/FreeCAD/FreeCAD/blob/145529fe741292ff0b3977a01195bf0247425794/src/Main/FreeCADGuiPy.cpp).

## Limiti

Non sono stati eseguiti una build da sorgente, installazione/discovery completa ET UX dopo riavvio, test desktop, rendering OpenGL, Nxt/Ribbon in funzione o test multipiattaforma. L'import QtQuick dimostra un prerequisito disponibile, non compatibilità Nxt. Runtime preparato, bozza di configurazione salvata e pubblicazione dell'ambiente sono stati distinti: la pubblicazione spetta all'utente.
