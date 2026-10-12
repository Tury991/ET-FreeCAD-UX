# ET-FreeCAD-UX

Workbench Python sperimentale per rendere **organizzazione dei comandi e workflow** di FreeCAD più familiari a chi usa SolidWorks, mantenendo il modello parametrico e le API native di FreeCAD. Il progetto non modifica il sorgente di FreeCAD e non è affiliato a SolidWorks o Dassault Systèmes.

## Stato iniziale

Il repository originale conteneva soltanto questo titolo, senza codice, manifest o test. Questa prima base introduce registrazione della workbench, un menu e una toolbar `ET UX`, un comando informativo nel pannello Report e test del ciclo di vita. Non implementa ancora ribbon, modellazione guidata, task panel, gestione degli assiemi o scorciatoie personalizzate.

La scelta iniziale è una **workbench autonoma con UI standard**, predisposta concettualmente a un adattatore opzionale FreeCAD-Ribbon. Nessun codice Ribbon è incorporato e nessun addon esterno è richiesto. Motivazioni e confronto: [studio Ribbon](docs/FREECAD_RIBBON.md).

## Installazione manuale di sviluppo

1. Usa FreeCAD **1.0.x** come baseline iniziale. Python è quello incluso in FreeCAD; i test puri richiedono Python 3.8 o successivo. Non installare un secondo binding Qt nel Python di FreeCAD.
2. Nella console Python di FreeCAD, esegui `print(App.getUserAppDataDir())` per trovare la directory utente effettiva.
3. Chiudi FreeCAD. Colloca o collega questa intera directory in `<directory utente>/Mod/ET-FreeCAD-UX`, con `InitGui.py` direttamente nella root dell'addon. Se esiste già una directory, preservala prima di sostituirla. Su Windows una copia è sufficiente; il collegamento è facoltativo.
4. Riavvia FreeCAD e seleziona **ET FreeCAD UX**. Il menu `ET UX → Informazioni su ET FreeCAD UX` scrive versione e scopo nel pannello Report (Visualizza → Pannelli → Report).
5. Per rimuoverla, chiudi FreeCAD e rimuovi solo la copia o il collegamento dell'addon dalla directory `Mod`. Non viene salvata una configurazione globale ET UX.

Per i task cloud usa il checkout esistente, senza creare worktree salvo richiesta esplicita. Non è ancora prevista distribuzione tramite Addon Manager: metadati `package.xml`, licenza e matrice multipiattaforma vanno completati prima della pubblicazione.

## Verifiche

Dalla root del repository, senza FreeCAD e senza dipendenze aggiuntive:

```sh
python3 -m unittest discover -s tests -v
```

Nella console Python di FreeCAD già avviato, con il percorso assoluto del checkout:

```python
import runpy
runpy.run_path('/percorso/ET-FreeCAD-UX/tools/smoke_freecad.py', run_name='__main__')
```

Lo smoke test registra la workbench, verifica menu, toolbar e comando e ripete tre attivazioni/disattivazioni, ripristinando la workbench precedente. Usare una sessione di sviluppo: la registrazione resta nella sessione fino alla chiusura. Il test non modifica documenti.

Nell'ambiente cloud Debian attuale, è stato verificato anche questo comando dalla root:

```sh
QT_QPA_PLATFORM=offscreen /usr/bin/python3 - <<'PY'
import sys, runpy
sys.path[:0] = ['/usr/lib/freecad-python3/lib', '/usr/share/freecad/Ext']
runpy.run_path('tools/smoke_freecad.py', run_name='__main__')
PY
```

Questi percorsi sono specifici della macchina Debian, non parte del loader dell'addon. Il Python predefinito della macchina non coincide con quello di FreeCAD. `freecadcmd` nella macchina attuale va in segfault nativo prima dell'esecuzione Python; lo smoke usa i moduli di sistema. Qt offscreen segnala avvisi di layout/font e la sessione GUI minimale segnala `Std_AddonMgr` non caricato: il test non richiede Addon Manager. L'esito atteso è `ETUX_GUI_SMOKE_OK` e codice di uscita 0.

Verificati: 4 test unitari e smoke GUI offscreen su FreeCAD 1.0.0, Python 3.13, Qt5/PySide2. Non verificati: installazione tramite loader completo dopo riavvio, interazione visiva desktop, Windows, macOS, Qt6, coesistenza runtime con Ribbon. Il supporto a FreeCAD 0.21 o versioni successive a 1.0 è un obiettivo da validare, non una garanzia.

## Struttura

```text
Init.py / InitGui.py       ingressi FreeCAD, senza side effect sul documento
et_freecad_ux/
  core/catalog.py         gruppi di comandi immutabili, Python puro
  adapters/freecad.py     registrazione e accesso alle API host
  ui/workbench.py         lifecycle e menu/toolbar standard
Resources/icons/etux.svg   icona originale del progetto
tests/                    contratti host con fake e test senza GUI
tools/smoke_freecad.py     verifica sulle API reali di FreeCAD
docs/ARCHITECTURE.md       confini, workflow e compatibilità
docs/ROADMAP.md            milestone con criteri di accettazione
docs/FREECAD_RIBBON.md     ricerca e decisione iniziale
AGENTS.md                 regole per i contributi futuri
```

Leggi [architettura](docs/ARCHITECTURE.md) e [roadmap](docs/ROADMAP.md) prima di introdurre funzionalità. La licenza del progetto è ancora da definire prima della distribuzione; l'assenza di `LICENSE` non concede una licenza open source. La base è scritta per questo repository, senza codice o asset copiati da SolidWorks o Ribbon.
