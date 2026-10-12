# ET-FreeCAD-UX

Workbench Python sperimentale per rendere **organizzazione dei comandi e workflow** di FreeCAD più familiari a chi usa SolidWorks, mantenendo il modello parametrico e le API native di FreeCAD. Il progetto non modifica il sorgente di FreeCAD e non è affiliato a SolidWorks o Dassault Systèmes.

## Stato iniziale

Il repository originale conteneva soltanto questo titolo, senza codice, manifest o test. Questa prima base introduce registrazione della workbench, un menu e una toolbar `ET UX`, un comando informativo nel pannello Report e test del ciclo di vita. Non implementa ancora ribbon, modellazione guidata, task panel, gestione degli assiemi o scorciatoie personalizzate.

La scelta iniziale è una **workbench autonoma con UI standard**, predisposta concettualmente a integrazioni opzionali FreeCAD-Ribbon e FreeCAD-Nxt. Nessun codice Ribbon è incorporato e nessun addon esterno è richiesto. Motivazioni: [confronto Nxt/Ribbon](docs/EXTENSIONS_COMPARISON.md) e [studio Ribbon](docs/FREECAD_RIBBON.md). La strategia pre-V0.2 non aggiunge funzioni di modellazione alla V0.1.

## Installazione manuale di sviluppo

1. Usa FreeCAD **1.1.3** come riferimento principale; FreeCAD 1.0 resta una compatibilità secondaria verificata nei limiti della matrice di test. Python è quello incluso in FreeCAD; i test puri richiedono Python 3.8 o successivo. Non installare un secondo binding Qt nel Python di FreeCAD.
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
runpy.run_path('/percorso/ET-FreeCAD-UX/tools/smoke_freecad.py', run_name='etux_gui_smoke')
```

Lo smoke test registra la workbench, verifica menu, toolbar e comando e ripete tre attivazioni/disattivazioni, ripristinando la workbench precedente. Usare una sessione di sviluppo: la registrazione resta nella sessione fino alla chiusura. Il test non modifica documenti.

## Runtime cloud FreeCAD 1.1.3

Installazione affiancata all'1.0 di sistema, fuori dal checkout, senza privilegi di amministratore:

```sh
bash tools/install_freecad113.sh
bash tools/test_freecad113.sh
```

Il primo script scarica l'AppImage ufficiale Linux x86_64, verifica il SHA256 fissato e la estrae senza FUSE in `/workspace/.local/freecad/1.1.3`. Il secondo usa **il Python dell'AppImage**, un profilo XDG temporaneo e Qt offscreen. Non installa binding Qt da pip e non sostituisce il FreeCAD di sistema. `ETUX_FREECAD_INSTALL_DIR` permette un percorso assoluto alternativo fuori dal checkout.

Esito atteso: `ETUX_RUNTIME_TESTS_OK version=1.1.3 unit=4 geometry=4 gui=True` con exit code 0. Per verificare solo unitari e geometria: `bash tools/test_freecad113.sh --geometry-only`. La versione viene controllata prima dei test: un 1.0 caricato al posto di 1.1.3 fallisce esplicitamente.

La compatibilità secondaria 1.0 si verifica nella macchina Debian con:

```sh
profile="$(mktemp -d /tmp/etux-freecad10.XXXXXX)"
XDG_CACHE_HOME="$profile/cache" XDG_CONFIG_HOME="$profile/config" XDG_DATA_HOME="$profile/data" \
  /usr/bin/python3 tools/check_freecad_runtime.py \
  --expect-version 1.0.0 --lib-dir /usr/lib/freecad-python3/lib --ext-dir /usr/share/freecad/Ext
result=$?
rm -rf "$profile"
exit "$result"
```

Questi percorsi 1.0 sono specifici della macchina Debian. Eseguire il blocco in una shell dedicata perché `exit` ne preserva l'esito. Il Python predefinito della macchina non coincide con quello del runtime CAD.

**Verificati su Linux x86_64:** 4 test unitari originali, 4 test geometrici (solido, differenza booleana, Undo/Redo, roundtrip FCStd) e smoke GUI offscreen sia su 1.1.3/Qt6 sia su 1.0.0/Qt5. I test geometrici esercitano le API native in documenti temporanei, senza modificare il motore geometrico. Dettagli, requisiti, checksum e problemi risolti: [runtime cloud](docs/FREECAD_113_CLOUD.md) e [requisiti](docs/REQUIREMENTS.md).

**Non verificati:** installazione tramite loader completo dopo riavvio, interazione visiva desktop, Windows/macOS e coesistenza runtime con Ribbon/Nxt. L'import dei moduli QtQuick nell'AppImage è verificato; non dimostra che Nxt o le sue superfici QML funzionino. Il supporto a versioni diverse da quelle della matrice non è una garanzia.

## Struttura

```text
Init.py / InitGui.py       ingressi FreeCAD, senza side effect sul documento
et_freecad_ux/
  core/catalog.py         gruppi di comandi immutabili, Python puro
  adapters/freecad.py     registrazione e accesso alle API host
  ui/workbench.py         lifecycle e menu/toolbar standard
Resources/icons/etux.svg   icona originale del progetto
tests/                    contratti host con fake e test senza GUI
tools/                    installazione runtime, runner e smoke host
docs/ARCHITECTURE.md       confini, workflow e compatibilità
docs/ROADMAP.md            milestone con criteri di accettazione
docs/FREECAD_RIBBON.md     ricerca e decisione iniziale
docs/FREECAD_NXT.md        analisi statica dei componenti Nxt
docs/EXTENSIONS_COMPARISON.md  strategia di riuso, licenze e compatibilità
docs/FREECAD_113_CLOUD.md  runtime e risultati riproducibili
docs/REQUIREMENTS.md       requisiti principali e opzionali
AGENTS.md                 regole per i contributi futuri
```

Leggi [architettura](docs/ARCHITECTURE.md) e [roadmap](docs/ROADMAP.md) prima di introdurre funzionalità. La licenza del progetto è ancora da definire prima della distribuzione; l'assenza di `LICENSE` non concede una licenza open source. La base è scritta per questo repository, senza codice o asset copiati da SolidWorks o Ribbon.
