# Verifica V0.4b — 15 ottobre 2026

Base `main` `d71d51889a8320e3632983e42ce343c4d155037b`, verificata via connettore
GitHub. Il ref locale `origin/main` era obsoleto; il branch dedicato parte dal
commit `main` effettivo già disponibile nel checkout. Il fetch/push Git HTTPS
non è disponibile per errore di connessione al proxy; consegna tramite API GitHub.

## Prove eseguite

| Ambiente | Unitari | Geometria nativa | GUI, diagnostica, cleanup |
| --- | --- | --- | --- |
| Python Linux senza FreeCAD/Qt | 25 casi: 24 passati, 1 skip PowerShell assente | Non applicabile | Import e failure path senza host/Qt |
| FreeCAD 1.1.3 ufficiale, Python 3.11.14, Qt6 6.8.3 | 24 passati, 1 skip | 8 passati | Passati a devicePixelRatio 1.0, 1.25, 1.5 |
| FreeCAD 1.0.0 Debian, Python 3.13.5, Qt5 5.15.15 | 24 passati, 1 skip | 8 passati | Passati a devicePixelRatio 1.0 |

Ogni avvio host usa profili XDG temporanei e il runner con controllo esatto di
versione. I tre avvii 1.1.3 usano `QT_SCALE_FACTOR=1`, `1.25`, `1.5`. Il layout
richiede finestre 1920×1080, 1600×900 e 1366×768 in pixel equivalenti, convertiti
in coordinate logiche con il rapporto Qt effettivo, più una finestra stretta.
Queste simulazioni offscreen non equivalgono alla scala display Windows reale.

Per ciascun avvio: **384 controlli scheda/layout** su due palette sintetiche,
font 100/125/150%, quattro passaggi Classic/Compact, quattro dimensioni e quattro
schede; 1152 casi su 1.1.3, più 384 su 1.0. Verificati:

- Pulsanti non inferiori alle metriche minime, nessun taglio verticale,
  scorrimento e visibilità dei comandi, inclusi quelli raggiunti con focus.
- Compact con altezza minore di Classic; stessa toolbar, stessa sequenza di
  pulsanti/QAction e scheda conservata durante i cambi densità.
- Palette/font realmente propagati ai widget; contrasto testo/sfondo almeno
  4,5:1 e accento focus/sfondo almeno 3:1 nelle due palette del test. Il test non
  certifica colori di ogni tema host né contrasto di tutte le icone native.
- Abilitazione e tooltip uguali alle azioni originali; focus forte, frecce tra
  schede, Tab tra comandi, scelte dal menu Ribbon e selezione esclusiva visibile.
- Cinque toggle, cinque cambi workbench, attivazione rapida annullata, chiusura;
  cancellazione di timer/filtro/widget e riferimenti, nessun duplicato.
- Ripristino dimensioni/visibilità delle toolbar ET UX e integrità di una
  toolbar estranea e dei dock nativi; fallback su toolbar mancante/Qt assente.
- Dispatch Body dalla Ribbon, creazione sketch e task Pad nativi; sei cambi
  densità con task Pad aperto senza sostituzione del task o della feature.
- Persistenza della sola densità ET UX via ParamGet e fallback per valori
  sconosciuti; cambi con Ribbon spenta senza import Qt. Catalogo 24+2 preservato.

## Comandi riproducibili

```sh
python3 -m unittest discover -s tests -v
bash tools/test_freecad113.sh
QT_SCALE_FACTOR=1.25 bash tools/test_freecad113.sh
QT_SCALE_FACTOR=1.5 bash tools/test_freecad113.sh
```

Regressione 1.0 con i soli moduli del sistema e profilo temporaneo:

```sh
profile_dir=$(mktemp -d /tmp/etux-freecad10.XXXXXX)
trap 'rm -rf "$profile_dir"' EXIT
XDG_CACHE_HOME="$profile_dir/cache" XDG_CONFIG_HOME="$profile_dir/config" \
XDG_DATA_HOME="$profile_dir/data" /usr/bin/python3 tools/check_freecad_runtime.py \
  --expect-version 1.0.0 --lib-dir /usr/lib/freecad-python3/lib \
  --ext-dir /usr/share/freecad/Ext
```

Marcatori finali osservati, exit code 0 per ciascun avvio:

```text
ETUX_MODERN_LAYOUT_OK cases=384 themes=2 font_scales=3 dpr=1.0
ETUX_RIBBON_SMOKE_OK toggles=5 switches=5 native_actions=26
ETUX_GUI_SMOKE_OK native_commands=24 groups=4 body=True sketch_dispatch=True pad_dispatch=True
ETUX_DIAGNOSTIC_OK
ETUX_RIBBON_CLOSE_OK
ETUX_RUNTIME_TESTS_OK version=1.1.3 unit=25 geometry=8 gui=True
ETUX_RUNTIME_TESTS_OK version=1.0.0 unit=25 geometry=8 gui=True
```

Gli altri avvii riportano `dpr=1.25` e `dpr=1.5`. `git diff --check` passa.
I log completi rimangono in `work/`, senza includere percorsi personali nella PR.
Le [quattro catture](screenshots/v0.4b/README.md) sono widget reali **offscreen**,
con palette sintetiche e ritaglio della sola Ribbon. Le tavole V0.4a sono mockup.

## Correzioni emerse e limiti

Il confronto visivo ha trovato la propagazione incompleta della palette:
Qt manteneva alcuni foreground precedenti nel cache stylesheet. Il renderer
ora aggiorna solo i widget ET UX e risolve nuovamente i colori dall'host.
Il focus su SubShapeBinder fuori viewport ora provoca scroll locale.
Qt5 richiedeva invalidazione/attivazione esplicita dei layout annidati e reset
dei minimi precedenti per ridurre correttamente Compact dopo un cambio font.
La diagnostica è stata aggiornata all'ordine Features/Sketch delle schede.
I tentativi con queste anomalie non sono conteggiati come prove superate.

**Non eseguiti:** PowerShell (assente), Windows interattivo 10/11, installazione
V0.4b dal loader dopo riavvio su Windows, multi monitor, temi FreeCAD completi,
accessibilità con screen reader e collaudo manuale geometrico completo.
I due nuovi casi PowerShell coprono upgrade da marker V0.3b senza nuova mappa
Ribbon e rifiuto di una sorgente V0.4b incompleta; richiedono CI/Windows o pwsh.
Il test upgrade usa un fixture del contratto V0.3b, non un desktop aggiornato.

Il comportamento Sketcher/ritorno accettato dall'utente non è stato modificato.
La prova automatica dispatch non sostituisce il percorso interattivo Windows.
Gli avvisi OpenGL/propagateSizeHints dell'offscreen restano attesi: nessuna
certificazione del viewport. Coesistenza con Ribbon/Nxt non provata. Installer,
backup e rimozione conservano il flusso esistente; la verifica dei nuovi casi
PowerShell resta necessaria prima di dichiararne il collaudo Windows completo.

Nel bootstrap minimale Debian 1.0 compare anche `ModuleNotFoundError:
AttachmentEditor` da un loader host: non è un fallimento degli assert ET UX,
ma il dispatch dei task di attachment/Reference non è stato certificato in
questo avvio. Le azioni Reference sono conservate e raggiungibili; provarne i
task sul desktop con installazione completa resta parte del collaudo manuale.
