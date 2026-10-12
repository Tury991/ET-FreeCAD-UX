# Verifica V0.2 — Mechanical Workspace

Eseguita il **12 ottobre 2026 (Europe/Rome)** nel cloud Linux x86_64. Base: ultimo `main` verificato via API GitHub, commit `f105516b5aff70992d5a50cde1f169496ea3641b`. Branch: `feature/mechanical-workspace-v0.2`. Il checkout iniziale aveva lo stesso tree `91170e7b3ba2e8120580681f3042fb8303733396`; l'oggetto merge di main è stato recuperato via API e verificato contro il suo SHA prima dello sviluppo. Git HTTPS non era raggiungibile dal proxy; pubblicazione tramite API GitHub, senza modificare main.

## Risultati finali

| Prova realmente eseguita | 1.1.3 ufficiale / Qt6 | 1.0.0 Debian / Qt5 |
| --- | --- | --- |
| Unitari in processo isolato | 8 passati | 8 passati |
| Geometria e documenti nativi | 8 passati | 8 passati |
| Registro: 24 azioni native richieste | Tutte presenti | Tutte presenti |
| GUI offscreen: menu e 4 toolbar, tre cicli senza duplicati | Passato | Passato |
| Comando Body e Body attivo | Passato | Passato |
| Comando NewSketch con piano origine selezionato | Passato | Passato |
| Pad nativo: selezione profilo e apertura task | Passato | Passato |
| Exit code del runner completo | 0 | 0 |

Eseguito anche `python3 -m unittest discover -s tests -v` con il Python predefinito: **8/8 passati**. Nessun fallimento finale o test saltato nelle suite indicate. Verificato anche il controllo versione: richiedere 1.1.3 con le librerie 1.0.0 produce la diagnosi esplicita e exit code 1 prima delle suite. `git diff --check` passa. Le iterazioni iniziali hanno rilevato e corretto errori nel test Qt, nella chiamata a `Gui.Command.get(...).isActive()` e nei percorsi/loader del bootstrap 1.0; non vengono conteggiate come verifiche positive.

Output finali:

```text
ETUX_GUI_SMOKE_OK native_commands=24 groups=4 body=True sketch_dispatch=True pad_dispatch=True
ETUX_RUNTIME_TESTS_OK version=1.1.3 unit=8 geometry=8 gui=True
ETUX_RUNTIME_TESTS_OK version=1.0.0 unit=8 geometry=8 gui=True
```

## Cosa dimostrano i test

Gli unitari controllano import senza FreeCAD/Qt, registrazione idempotente anche dopo reload, inizializzazione/attivazioni ripetute, comandi informativi senza documento, filtro delle capacità, ordine dei gruppi, diagnosi dei comandi assenti e caricamento parziale se un modulo fallisce.

Gli 8 geometrici includono le 4 prove precedenti (Box, booleano, Undo/Redo, roundtrip FCStd) e 4 nuove: Body; sketch con vincolo di raggio nel Body; Pad parametrico con profilo collegato e volume analitico; modifica del raggio da 5 a 7 mm con ricalcolo del Pad e Undo/Redo. Il Pad è lungo 10 mm: volumi circa 785,398 e 1539,380 mm³. Questi test usano le API modello native, non click GUI.

Lo smoke GUI verifica i comandi reali, numero di azioni per toolbar, quattro sottomenu e assenza di duplicati dopo tre cambi workbench. Crea un documento temporaneo, invoca Body e NewSketch sul piano XY, costruisce un cerchio vincolato con le API modello, seleziona lo sketch e invoca Pad. Verifica che il task sia aperto, il profilo corretto e il solido valido. Termina il task temporaneo e chiude il documento; ripristina workbench, documento e selezione precedenti. Rifiuta l'avvio se c'è già un task aperto.

## Riproduzione

```sh
python3 -m unittest discover -s tests -v
bash tools/test_freecad113.sh
```

Per 1.0 usa il blocco XDG temporaneo in [FREECAD_113_CLOUD.md](FREECAD_113_CLOUD.md) o README con `/usr/bin/python3`, `/usr/lib/freecad-python3/lib` e `/usr/share/freecad/Ext`. Il runner carica soltanto moduli e loader del runtime selezionato; versione errata o suite fallita produce exit code non zero.

## Limiti non verificati

- Windows/macOS e sessione desktop interattiva Linux; procedura manuale nel README.
- Loader completo di ET UX da `Mod` dopo riavvio, DPI, temi, shortcut e navigazione da tastiera.
- Rendering OpenGL, disegno via mouse, conferma/annullamento interattivo di tutti i task e percorsi con più documenti/Body.
- Operazioni Pocket, Fillet, Chamfer, Revolution e Reference: disponibilità reale verificata, geometria e interazione specifiche non esercitate automaticamente.
- Coesistenza runtime con Ribbon/Nxt e versioni host diverse dalle due build provate.

Qt offscreen emette avvisi sul contesto OpenGL e su `propagateSizeHints`; 1.1.3 segnala anche QThreadStorage in chiusura. Il bootstrap minimale 1.0 segnala moduli accessori (Profiles/InvoluteGear/Sprocket/AddonMgr) non caricati. Le azioni del catalogo e le asserzioni sopra passano; gli avvisi non dimostrano qualità del viewport. Nessun addon terzo o binding Qt pip è stato installato.

La workbench non scrive preferenze, non modifica FreeCAD e non duplica il motore. Licenza e metadati di distribuzione restano da definire. La PR deve essere revisionata; nessun merge automatico.
