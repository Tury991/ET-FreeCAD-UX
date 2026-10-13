# Verifica V0.3a — Ribbon sperimentale

12 ottobre 2026 (Europe/Rome), cloud Linux x86_64, base remoto `main`
`6a401f71760ac82b8371589cb9a58c15c95deb25`. Prototipo originale ET UX;
nessun addon terzo o binding pip installato. Nessuno screenshot prodotto.

| Livello | FreeCAD 1.1.3 ufficiale | FreeCAD 1.0.0 Debian |
| --- | --- | --- |
| Python e Qt | Python 3.11.14, Qt/PySide6 6.8.3 | Python 3.13.5, Qt/PySide2 5.15.15 |
| Unitari, fake host | 14 passati | 14 passati |
| Geometria nativa | 8 passati | 8 passati |
| GUI offscreen V0.2 e Ribbon | passata, exit 0 | passata, exit 0 |
| Desktop interattivo / loader completo da Mod | non eseguito | non eseguito |

Anche `python3 -m unittest discover -s tests -v` passa fuori dall'host. Gli
unitari verificano import senza Qt/FreeCAD, catalogo e registrazione, disponibilità,
failure path, restore delle dimensioni senza scrittura visibilità, cleanup ripetuto
e annullamento del timer. Sono contratti fake, non prove di rendering.

Le 8 prove geometriche V0.2 restano: solido, booleano, Undo/Redo parametri,
roundtrip FCStd, Body, sketch vincolato nel Body, Pad parametrico e raggio sketch
che ricalcola Pad con Undo/Redo. Il prodotto non implementa questi algoritmi.

Smoke con API/Qt reali, profilo XDG temporaneo e versione esatta:

- Disponibilità dei 24 comandi nativi e dei gruppi/menu V0.2, tre cambi iniziali
  senza duplicazione delle quattro toolbar.
- Cinque creazioni/distruzioni via comando toggle, doppia activate idempotente,
  quattro schede e identità delle 26 QAction V0.2 (24 native + guida/about).
- Compressione delle sole toolbar ET UX, visibilità e limiti min/max ripristinati,
  toolbar esterna sentinella intatta. Test anche con una toolbar inizialmente nascosta.
- Resize a 480 px; cinque cambi workbench con ricreazione, più cambio rapido
  prima del callback timer (nessuna riattivazione tardiva).
- Nuovo documento via API di test e Body via pulsante Ribbon dopo aggiornamento
  GUI nativo; comando e task nativi NewSketch/Pad V0.2 ancora verificati.
- Dock nativi non sostituiti; toolbar ET UX assente simulata con rename temporaneo:
  fallback senza widget residui e senza comprimere le altre toolbar.
- Chiusura reale della finestra nel runner: filtro Close elimina Ribbon e risorse;
  DeferredDelete drenato prima del teardown, exit code realmente 0.

Il runner usa un bootstrap GUI minimale con i soli loader ufficiali PartDesign
e Sketcher; non è il loader completo degli addon. Il sottoprocesso normalizza
argv per non far interpretare a FreeCAD il marcatore stdin Python come documento.
Lo smoke drena le cancellazioni possedute senza far partire indiscriminatamente
tutti i timer loader iniziali; `Gui.updateGui()` esercita l'aggiornamento host nei
cambi e prima del dispatch; un event loop limitato a 350 ms lascia al timer nativo
aggiornare l'abilitazione del pulsante Body, senza forzarla. Non sono automatizzate interazione tastiera/mouse
desktop, scelta dei piani, disegno a mano o accettazione interattiva dei task.

## Riproduzione

```sh
python3 -m unittest discover -s tests -v
bash tools/test_freecad113.sh
```

Per 1.0 usare il comando con profilo isolato in [FREECAD_113_CLOUD.md](FREECAD_113_CLOUD.md).
Il runner deve terminare con:

```text
ETUX_RIBBON_SMOKE_OK toggles=5 switches=5 native_actions=26
ETUX_GUI_SMOKE_OK native_commands=24 groups=4 body=True sketch_dispatch=True pad_dispatch=True
ETUX_RIBBON_CLOSE_OK
ETUX_RUNTIME_TESTS_OK version=1.1.3 unit=14 geometry=8 gui=True
```

Su 1.0 il marcatore finale riporta `version=1.0.0`. Log temporanei in `work/`,
non inclusi nel prodotto. Il comando di prova manuale smoke è nel README e crea
documenti temporanei; eseguire senza task aperti in una sessione di sviluppo.

## Limiti e accettazione desktop

Offscreen esercita widget e dispatch reali, non certifica ergonomia, viewport
OpenGL, DPI, temi, Linux desktop/Windows/macOS, loader dopo riavvio, preferenze
salvate dall'host su riavvio o coesistenza addon. Avvisi Qt offscreen/OpenGL e,
su Debian 1.0, moduli opzionali PartDesign incompleti non fanno fallire i 24 ID
richiesti: non sono prove della qualità del viewport. La diagnosi di toolbar
Sketch mancante è intenzionale nel failure test.

Restano da eseguire: installazione da Mod, demo README con/senza Ribbon,
documenti/Body multipli, sketch/task aperti, FCStd riaperto, Undo/Redo da UI,
chiusura annullata, riavvio/rimozione, configurazioni toolbar personalizzate,
temi/DPI e navigazione tastiera. Provare addon esterni singolarmente in profili
isolati, poi coesistenza con revisioni fissate. Non rendere il prototipo predefinito
prima di questi gate. Nessun merge automatico.
