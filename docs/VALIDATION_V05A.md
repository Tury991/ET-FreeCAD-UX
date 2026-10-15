# Verifica V0.5a — 15 ottobre 2026

## Aggiornamento PR #10 con main/PR #11

Integrato `main` **a9925e5bd48e4eded4a5e8208c5864d3ed905d55**, che include
la PR #11, nel branch `feat/v05a-mechanical-sketch-ribbon`. La V0.5a precedente
era al commit remoto **7fbe03cb0e97a107c4d18cb07db644037757da3b**.
Nessuna modifica ai sorgenti `et_freecad_ux`, loader, versione, catalogo,
renderer, observer o smoke di continuità Sketcher.

Il file `install-windows.ps1` è identico a quello di main/PR #11: default della
sorgente risolto nel corpo solo se omesso e valori esplicitamente vuoti rifiutati.
Conservati conferma, guardie, backup e rollback. La suite Windows combina tutti
i **20 casi** di main (inclusi `-File` reale senza `-SourceDirectory`, `-WhatIf`,
backup V0.4b e prima installazione) con il fixture storico già congelato in V0.5a.
Non si reintroduce il vecchio fixture ricavato dal catalogo corrente.

Regressioni rieseguite sul contenuto integrato:

| Ambiente | Esito |
| --- | --- |
| Python Linux | 36 unitari, 35 passati e 1 skip PowerShell assente |
| FreeCAD Linux 1.1.3 / Qt6 6.8.3 | 36 unitari (1 skip), 8 geometrici, 384 casi layout, quattro percorsi Sketch Ribbon, GUI/diagnostica/chiusura passati; exit code 0 |
| FreeCAD Linux 1.0.0 / Qt5 5.15.15 | Stesse suite passate; exit code 0; resta il limite host AttachmentEditor descritto sotto |

I quattro percorsi coprono Classic/Compact e palette chiara/scura, creazione e
modifica sketch, chiusura, task e QAction condivisi, vincolo nativo, Undo/Redo,
cambio volontario workbench, cambio/chiusura documento e cleanup. Comandi
riproducibili invariati nelle sezioni seguenti. `git diff --check` passa.

I risultati Windows rieseguiti sul nuovo commit e il collegamento alla CI sono
riportati nella [descrizione aggiornata della PR #10](https://github.com/Tury991/ET-FreeCAD-UX/pull/10).
Le sezioni seguenti conservano l'evidenza iniziale antecedente all'integrazione.
Nessuna dichiarazione di collaudo Windows interattivo; nessun merge della PR #10.

Base `main` V0.4b **ff2217a0e37cac6aa084ddbe6b5fa6033ebf21fe**,
verificata tramite connettore GitHub. Il checkout iniziale era V0.4a e il proxy
Git HTTPS non rispondeva: i file aggiornati sono stati recuperati via API,
verificando tutti gli hash blob, il tree `3ca973580a38489572c6fdb503620ff98a5aeff9`
e il commit firmato prima di creare il branch dedicato. Nessuna modifica installer.

## Prove eseguite

| Ambiente | Unitari | Geometria nativa | GUI offscreen |
| --- | --- | --- | --- |
| FreeCAD 1.1.3 ufficiale Linux, Python 3.11.14, Qt6 6.8.3 | 36 casi, 35 passati, 1 skip PowerShell assente | 8 passati | Layout, Sketch Ribbon, dispatch, diagnostica e chiusura passati |
| FreeCAD 1.0.0 Debian, Python 3.13.5, Qt5 5.15.15 | 36 casi, 35 passati, 1 skip PowerShell assente | 8 passati | Stesse verifiche passate; limite AttachmentEditor indicato sotto |

Entrambe le esecuzioni usano profili XDG temporanei, controllo esatto di versione,
processi distinti per fake e GUI nativa, namespace `__main__` host preservato.
Exit code 0. Nessun pacchetto Qt pip installato nell'host.

Per ciascun runtime:

- Registro reale: tutti i **41 ID nativi** presenti; **43 azioni** native/informative
  disponibili una sola volta nella mappa condivisa Classic/Compact.
- Suite V0.4b conservata: 384 casi di layout su due palette sintetiche, tre
  scale font, quattro passaggi densità e quattro dimensioni, a DPR 1.0;
  azioni condivise, tooltip/stato/focus, overflow, cleanup e fallback.
- Quattro percorsi sketch: Classic/Compact × palette chiara/scura; creazione
  nativa da piano XY attraverso QAction della Ribbon, modifica esistente,
  chiusura e ritorno nativo a ET UX con ripristino della scheda Features.
- Stessa Ribbon, stessi pulsanti/QAction e stesso task durante editing e cambi
  densità; strumenti di geometria attivi, stato di ogni pulsante uguale all'azione.
- Dispatch reale del vincolo orizzontale dalla Ribbon su una linea selezionata,
  Undo/Redo del vincolo nativo e di una geometria di setup; task non sostituito.
- Cambio volontario a PartDesign durante sketch: rimozione Ribbon e observer,
  timer cancellato, task ancora aperto, nessun ritorno ET UX imposto alla chiusura.
- Cambio manuale a Sketcher senza editing: cleanup, nessuna riapparizione per
  uno sketch aperto successivamente; ritorno esplicito a ET UX durante editing.
- Disattivazione Ribbon durante sketch e chiusura tramite il **vero pulsante
  Close del task Qt**, che esegue `TaskDlgEditSketch::reject`; nessuna riapparizione.
  Questo non simula il disegno col mouse o Escape e non dimostra rollback globale.
- Cambio documento durante editing, chiusura del documento in modifica,
  nessun nome di sketch o timer obsoleto dopo teardown; cinque toggle e cinque
  cambi workbench nella suite preesistente, nessun duplicato di toolbar/dock.
- Unitari nuovi: transizione confermata/non confermata, scelta volontaria,
  cambio documento, restore della scheda, ingresso con editor già aperto,
  cleanup idempotente e rimozione observer dopo errore parziale di registrazione.

## Comandi riproducibili

```sh
python3 -m unittest discover -s tests -v
bash tools/test_freecad113.sh
```

Per le catture reali della sola Ribbon:

```sh
ETUX_SCREENSHOT_DIR=/percorso/temporaneo bash tools/test_freecad113.sh
```

Regressione 1.0:

```sh
profile_dir=$(mktemp -d /tmp/etux-v05a-10.XXXXXX)
trap 'rm -rf "$profile_dir"' EXIT
XDG_CACHE_HOME="$profile_dir/cache" XDG_CONFIG_HOME="$profile_dir/config" \
XDG_DATA_HOME="$profile_dir/data" /usr/bin/python3 tools/check_freecad_runtime.py \
  --expect-version 1.0.0 --lib-dir /usr/lib/freecad-python3/lib \
  --ext-dir /usr/share/freecad/Ext
```

Marcatori osservati:

```text
ETUX_MODERN_LAYOUT_OK cases=384 themes=2 font_scales=3 dpr=1.0
ETUX_SKETCH_RIBBON_OK cases=4 native_commands=41 undo_redo=True
ETUX_RIBBON_SMOKE_OK toggles=5 switches=5 native_actions=43
ETUX_DIAGNOSTIC_OK
ETUX_RIBBON_CLOSE_OK
ETUX_RUNTIME_TESTS_OK version=1.1.3 unit=36 geometry=8 gui=True
ETUX_RUNTIME_TESTS_OK version=1.0.0 unit=36 geometry=8 gui=True
```

## Risultati, correzioni e limiti

La prima prova della continuità ha fallito: il segnale `workbenchActivated`
arriva prima dell'hook `Deactivated`, quando ancora non c'è `getInEdit`.
L'adapter ora identifica la transizione dal nome precedente nel segnale e
attende l'evento InEdit nativo prima della verifica differita. Le prove fallite
non sono contate come successi. I test attendono un turno **limitato** del timer
comandi host per controllare l'abilitazione; il prodotto non forza gli stati.

Le prime catture hanno inoltre mostrato la fascia stretta accanto alle toolbar
Sketcher: la versione finale inserisce la sola Ribbon su una propria riga e
rimuove la separazione durante il cleanup. Le [catture](screenshots/v0.5a/README.md)
sono widget reali offscreen 1.1.3, con palette sintetiche, non mockup o desktop.

Il runtime Debian 1.0 emette il precedente `ModuleNotFoundError: AttachmentEditor`
nel bootstrap minimale e avvisi di icone/loader; gli assert ET UX e l'exit code
passano. Non certifica i task Reference/attachment su tale bootstrap. Avvisi
OpenGL, `propagateSizeHints` e `QThreadStorage` sono presenti nell'offscreen:
nessuna validazione del viewport 3D o dell'interazione CAD col mouse.

**Non eseguiti:** Windows interattivo, aggiornamento reale Windows dalla V0.4b,
Escape/disegno col mouse, geometria finale di tutte le nuove feature/vincoli,
temi host completi, DPI fisici/multi monitor, screen reader e coesistenza Nxt/Ribbon.
La CI Windows della nuova PR non è inclusa in questi risultati locali.
Il [primo avvio CI](https://github.com/Tury991/ET-FreeCAD-UX/actions/runs/38710955577)
si è fermato nel fixture legacy degli script: il test eliminava il manifest
dal catalogo corrente, che dalla V0.5a non coincide più con una versione legacy.
Il test ora usa una copia congelata del catalogo V0.2–V0.4b, con SHA256
`b68d36663554a7150bee2b670e59966702fce965ab7d3e043396533bfd6d31e0`.
La guardia installer ha rifiutato correttamente la copia incoerente: nessuna
modifica installer o correzione della Issue #9. Il primo job CAD era saltato,
quindi non viene conteggiato come verifica Windows positiva.
La presenza degli ID non garantisce una feature valida per ogni selezione.
Il task Sketcher espone Close, non un pulsante Cancel con rollback globale.
Il [collaudo manuale](RIBBON_V05A.md#checklist-manuale-windows-1011) copre i gate aperti.
