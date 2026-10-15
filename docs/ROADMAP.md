# Roadmap

| Milestone | Stato e ambito | Gate |
| --- | --- | --- |
| V0.1 — fondazione | Completata: loader, catalogo puro, adapter, comando informativo, infrastruttura runtime | Base del Mechanical Workspace |
| V0.2 — Mechanical Workspace | Implementata: Sketch, Features, Reference, Tools; azioni native; disponibilità e guida; test Body/Sketch/Pad/ricalcolo e GUI offscreen | Risultati in [VALIDATION_V02.md](VALIDATION_V02.md); accettazione desktop ancora aperta |
| V0.2 — accettazione desktop | Da eseguire: installazione da Mod dopo riavvio, demo manuale README, modifica task, più documenti/Body, FCStd, Undo/Redo | Linux e Windows reali, DPI/temi, navigazione da tastiera; nessun duplicato o preferenza riscritta |
| V0.3a — prototipo Ribbon | Implementato opt-in Qt/PySide locale, quattro schede, QAction V0.2, compressione reversibile delle sole toolbar ET UX, fallback standard | [Studio](RIBBON_V03A.md), unitari e smoke offscreen su 1.1.3/Qt6 e 1.0/Qt5; [verifica](VALIDATION_V03A.md). Esperienza desktop non certificata |
| V0.3a — accettazione desktop | Aperta: layout stretto/largo, tab e tastiera, temi chiaro/scuro, DPI, task e documenti, riavvio/rimozione, chiusura annullata | Demo V0.2 con/senza Ribbon; albero/proprietà invariati; niente duplicati o toolbar residue; nessuna preferenza alterata dopo riavvio |
| V0.3b — Windows First | Implementati installazione locale, update/backup, rimozione con conferma/link sicuri, export percorso profilo, diagnostica anonima e CI Windows | 16 prove script su PowerShell 5.1/7; FreeCAD 1.1.3 Windows Server 2025: 19 unitari, 8 geometrici e GUI/diagnostica offscreen passati. Regressioni Linux 1.1.3/1.0. [Risultati](VALIDATION_V03B.md) |
| V0.3b — collaudo Windows 10/11 | Aperto: installazione/aggiornamento/rimozione e demo con FreeCAD normalmente avviato, profili, policy, DPI/temi, tastiera e riavvio | Seguire [guida utente](WINDOWS_GUIDE.md), allegare solo JSON diagnostico anonimo; CI/offscreen non certifica desktop 10/11 |
| V0.4a — studio UX | Quattro concept Classic/Compact, chiaro/scuro; documentazione | [Studio e asset](UX_V04A.md), mockup distinti dal prodotto |
| V0.4b — Ribbon moderna | Implementate due densità dello stesso layout, gruppi, palette locale e preferenza ET UX persistente | [Verifica V0.4b](VALIDATION_V04B.md); accettazione Windows interattiva e temi desktop aperta |
| Distribuzione | Da definire: licenza, package.xml, Addon Manager e CI | Licenza approvata e matrice desktop verificata prima della distribuzione |
| Qualità UX | Futura: onboarding contestuale e preferenze opt-in, shortcut configurabili | Dimostrare riduzione degli errori e dei cambi workbench; non sovrascrivere shortcut |
| Ribbon/Nxt opzionali | Futuri esperimenti separati | Pin/API/licenze verificate, profili isolati, stesso workflow con/senza addon, rimozione reversibile |
| Altri domini | Assiemi, TechDraw e workflow distinti | Adapter e test dedicati; nessuna promessa di equivalenza universale |

La V0.2 usa solo menu e toolbar FreeCAD. Tree, inspector, gizmo, isolate e riparazioni sketch già native o presenti in Nxt non saranno duplicati senza motivazione verificabile. Il [confronto](EXTENSIONS_COMPARISON.md) e gli studi Nxt/Ribbon descrivono la ricerca pre-V0.2, non una certificazione della coesistenza.

FreeCAD 1.1.3 resta il riferimento esatto; 1.0 è una regressione secondaria. Aggiornamenti della versione host richiedono prove separate. L'offscreen non sostituisce i gate desktop. Non ampliare il prototipo in un editor Ribbon completo, solver, patch del kernel o integrazione automatica addon. Un adapter esterno richiederà API/schema versionati e coesistenza provata in profilo isolato.
