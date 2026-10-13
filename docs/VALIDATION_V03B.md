# V0.3b — evidenze di verifica

13 ottobre 2026 (Europe/Rome). Base: ultimo `main`
`1b39a64e0225eee66b41f1938cc102e58b71e16c`, merge V0.3a. Branch
`feature/windows-first-v0.3b`; main non modificato, nessun merge autonomo.
Git HTTPS cloud non risponde al proxy: base e pubblicazione via connettore
GitHub, mantenendo il checkout e i file della base esatta.

## Linux x86_64 — runtime effettivi

| Runtime | Unitari | Geometria | GUI offscreen + diagnostica |
| --- | --- | --- | --- |
| FreeCAD 1.1.3 ufficiale, Python 3.11.14, Qt6 6.8.3 | 19 casi, 18 passati + 1 skip | 8 passati | passata, exit 0 |
| FreeCAD 1.0.0 Debian, Python 3.13.5, Qt5 5.15.15 | 19 casi, 18 passati + 1 skip | 8 passati | passata, exit 0 |

Lo skip e **il bridge PowerShell**, assente nel cloud Linux: non si conta come
test degli script eseguito. Anche `python3 -m unittest discover -s tests -v`
fuori dall'host termina con 18 passati/uno skip. I test diagnostica fake verificano
registration assente non mascherata, task aperto senza mutazioni e mancata
esportazione di percorsi/nomi modello nelle eccezioni. Il manifest deve allineare
identita/schema/versione al prodotto.

Il runner effettivo mantiene le 8 prove geometriche e tutto lo smoke V0.3a
(azioni native, cinque toggle/cambi, fallback, dimensioni/visibilita ripristinate,
Body/NewSketch/Pad, task e chiusura). Aggiunge `run()` diagnostico reale con
registrazione, comandi, schede, toggle, cambio workbench e restore sessione.
Marcatori di successo:

```text
ETUX_RIBBON_SMOKE_OK toggles=5 switches=5 native_actions=26
ETUX_GUI_SMOKE_OK native_commands=24 groups=4 body=True sketch_dispatch=True pad_dispatch=True
ETUX_DIAGNOSTIC_OK
ETUX_RIBBON_CLOSE_OK
ETUX_RUNTIME_TESTS_OK version=1.1.3 unit=19 geometry=8 gui=True
```

Su 1.0 il marcatore versione e `1.0.0`. Avvisi offscreen/OpenGL e moduli opzionali
Debian restano limiti del bootstrap documentati in V0.3a, non prove di viewport.
Log locali in `work/`, esclusi dal prodotto.

## Windows CI — script PowerShell

Runner effettivo **Windows Server 2025**, immagine GitHub `windows-2025-vs2026`.
Windows PowerShell **5.1.26100.33438** e PowerShell **7.6.6**: suite iniziale
di 14 prove passata in entrambi i shell, poi ampliata a **16 prove** (legacy e
processo aperto simulato). Le 16 prove passano su entrambe dopo la correzione
dei newline Windows: il test legacy ha individuato CRLF diversi dallo ZIP LF,
ora normalizzati prima del confronto hash.

Evidenza finale, entrambi i job riusciti:
[run 38355985926](https://github.com/Tury991/ET-FreeCAD-UX/actions/runs/38355985926),
commit `ba11dd5ae77d8ce54cddbf21f6d0268ff619ca70`.
Il test legacy CRLF aveva fallito prima della correzione; il primo tentativo
CAD non selezionava univocamente il Python portable (esiste anche un launcher
venv). Il runner ora sceglie quello accanto a FreeCAD.pyd. Non sono stati ignorati
gli exit code dei fallimenti: il run finale termina con successo reale.

Le prove creano profili/fixture **temporanei**, non modificano il Mod reale o
preferenze utente: installazione, spazi/Unicode, update con backup fuori Mod,
riconoscimento legacy, guardia processo aperto simulato, copie incomplete,
directory/marker estranei, JSON/percorso invalidi, copia annidata, WhatIf senza
scritture, conservazione vecchia copia dopo errore, rimozione idempotente,
backup/altre workbench intatti, junction root senza cancellare target e rifiuto
di junction Mod/link interni. Nessun Pester, pip, admin o policy modificata.

## FreeCAD Windows e desktop

Il job native offscreen usa l'archivio portable ufficiale 1.1.3 con SHA256 fissato
e il Python/Qt incluso, in profilo temporaneo. **Passato su Windows Server 2025:**
FreeCAD 1.1.3, Python 3.11.14, Qt/PySide6 6.8.3, OpenCASCADE 7.8.1;
19 unitari passati (nessuno skip, incluso bridge PowerShell con 16 prove),
8 geometrici e smoke GUI/Ribbon/diagnostica/Close passati, exit 0. Marcatori
identici a quelli sopra, incluso `ETUX_DIAGNOSTIC_OK`. Nessun binding esterno.

Questo e un runtime CAD reale **su Windows**, ma con bootstrap/offscreen:
non equivale all'esperienza desktop normalmente avviata dall'eseguibile FreeCAD.
FreeCAD 1.0 su Windows non e stato provato (regressione secondaria Linux passata).

**Non eseguiti:** desktop interattivo Windows 10/11, editor macro/menu effettivo,
loader completo da Mod, riavvio installazione/update/remove su macchina utente,
policy aziendali, OneDrive/ACL/file bloccati, DPI/temi/tastiera, crash durante
update/rollback e coesistenza addon. La conferma usa il contratto PowerShell
standard; i test automatizzati esercitano `-WhatIf` e opt-out esplicito
`-Confirm:$false`, non l'interazione Y/S al prompt utente.

La [guida Windows](WINDOWS_GUIDE.md) e il piano di accettazione da eseguire,
non un verbale di verifica desktop. Nessuno screenshot prodotto. Nessuna
compatibilita Windows 10/11 certificata sulla sola base Linux/CI Server.
