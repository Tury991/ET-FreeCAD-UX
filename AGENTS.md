# Indicazioni per gli agenti e i contributori

## Obiettivo e limiti

ET-FreeCAD-UX è una workbench Python per migliorare la UX di FreeCAD con workflow familiari agli utenti SolidWorks. Usa API pubbliche e comandi nativi. Non modificare il sorgente di FreeCAD, fare monkey patch di classi host o copiare codice, icone e branding SolidWorks. La base iniziale deve restare piccola: non anticipare le milestone senza una richiesta.

## Architettura

- `core/`: Python puro, senza import di FreeCAD, FreeCADGui o Qt, senza I/O e stato globale mutabile.
- `adapters/`: accesso alle API host, dipendenze iniettate e controlli di disponibilità. Isola qui eventuali differenze tra versioni.
- `ui/`: presentazione e lifecycle. Importa host/Qt solo quando serve la GUI; usa il binding fornito da FreeCAD, mai installazioni pip di PyQt/PySide nell'host.
- `Init.py` non deve dipendere dalla GUI. `InitGui.py` deve limitarsi alla registrazione. I comandi del progetto hanno prefisso `ETUX_`.
- Un futuro backend Ribbon è opzionale e separato: non importarlo all'avvio e non copiarne il codice. La UI standard resta utilizzabile senza addon.
- Nessun componente può nascondere toolbar di altre workbench, sostituire menu globali o riscrivere preferenze senza una funzione esplicita, reversibile e testata.
- Observer, timer, connessioni Qt e widget futuri devono avere un proprietario e cleanup idempotente su disattivazione, cambio documento e chiusura. Non mantenere riferimenti a documenti chiusi.
- Non duplicare algoritmi CAD. Se si modificano documenti, aggiungere transazioni Undo/Redo e test di annullamento; i comandi nativi devono mantenere la propria gestione delle transazioni.

## Metodo e verifica

Usa il checkout esistente nei task cloud; non creare worktree salvo richiesta. Controlla `git status` e preserva il lavoro altrui. Durante solo onboarding non modificare sorgenti, test, manifest o lockfile; una richiesta esplicita di sviluppo autorizza modifiche pertinenti al progetto.

Prima di proporre modifiche leggi README e documenti in `docs/`. Mantieni documentazione italiana e nomi API in inglese. Nessuna dipendenza esterna è necessaria per la base.

Esegui dalla root `python3 -m unittest discover -s tests -v`. Per modifiche a loader/lifecycle/comandi esegui anche `tools/smoke_freecad.py` nelle modalità documentate nel README. Verifica che i test siano realmente eseguiti; non confondere fake con validazione host. Un test GUI offscreen non dimostra ergonomia desktop o compatibilità multipiattaforma.

Aggiungi test che verificano comportamento e failure path quando introduci logica di workflow. Non limitarti a test che rispecchiano righe d'implementazione. Aggiorna roadmap e compatibilità solo con evidenze; distingui obiettivi da versioni testate. Non eseguire codice di addon terzi per una ricerca senza necessità e senza profilo isolato.

Prima di incorporare dipendenze, verifica licenze e provenienza. La licenza ET UX è da decidere prima della distribuzione; non dichiarare compatibilità di licenza Ribbon finché l'incoerenza GPL/LGPL descritta nello studio non è chiarita.
