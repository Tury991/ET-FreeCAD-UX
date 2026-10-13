# V0.3b — deployment Windows e diagnostica

Il codice CAD/UI V0.1–V0.3a e il catalogo di 24 comandi nativi restano invariati.
La versione prodotto diventa `0.3.0b1`. Gli strumenti Windows sono separati da
loader, core e renderer; non vengono importati all'avvio della workbench.

## Contratto di installazione locale

- `install-windows.ps1` e `uninstall-windows.ps1`: Windows PowerShell >=5.1,
  API .NET e cmdlet inclusi, nessun modulo da installare, download o elevazione.
- `tools/windows/ETUX.Windows.psm1`: guardie condivise e payload consentito.
  La destinazione si costruisce esclusivamente come
  `<FreeCAD user app data>/Mod/ET-FreeCAD-UX`; non esiste un parametro libero per
  cancellare un'altra directory. Tutti i cmdlet filesystem usano `-LiteralPath`;
  le API .NET ricevono stringhe complete. Spazi/Unicode sono testati in CI.
- `tools/export_user_directory.FCMacro`: usa `App.getUserAppDataDir()` nella GUI
  reale, salva schema/application/version/user_app_data_dir tramite dialogo.
  Nessuna preferenza viene scritta. Il file privato viene passato con
  `-UserDataFile` o trovato accanto agli script come `freecad-user-path.json`.
  Alternativa esplicita: `-FreeCADUserDir`, assoluto e verificato dall'utente
  nella console host. Non vengono indovinati APPDATA, registro o installazioni.
- `etux-package.json`: ID `Tury991/ET-FreeCAD-UX`, schema 1 e versione allineata
  al prodotto. Identifica la copia, non e una firma, una licenza o un manifest
  Addon Manager. Per legacy senza marker si verificano i file runtime e hash
  noti del loader/catalogo V0.1/V0.2/V0.3a. Hash su UTF-8 normalizzato CRLF→LF,
  perche Git Windows puo convertire newline rispetto allo ZIP. Copie legacy
  modificate/non riconosciute sono rifiutate, non sovrascritte.

Il pacchetto copia solo root file espliciti, `et_freecad_ux`, `Resources`, `docs`
e `tools`. `.git`, `tests`, `work`, JSON profilo privato e log root non entrano
nell'installazione. Vengono verificati Init/InitGui, tutti i moduli runtime, icona,
helper, macro, diagnostica e guida. Non si mescolano file di versioni diverse.

`SupportsShouldProcess`/`ConfirmImpact=High` forniscono conferma sul percorso
concreto prima delle operazioni e `-WhatIf` senza scritture. `-Confirm:$false`
e disponibile solo come opt-out esplicito PowerShell (usato nei test isolati),
non come default del collaudo utente. FreeCAD/FreeCADCmd aperti bloccano l'operazione.

## Staging, aggiornamento e rollback

Prima di mutare la destinazione: validazione profilo/copia, guardie link e identita
dell'installazione esistente. Dopo conferma: copia in
`<profilo>/ETUX-Backups/.etux-stage-<data>-<guid>`, verifica, ricontrollo target,
rename dell'installazione vecchia in `ET-FreeCAD-UX-<data>-<guid>` e rename dello
staging in Mod. I backup non sono workbench aggiuntive caricabili da Mod.

Il vecchio pacchetto non viene cancellato. Se fallisce dopo il rename, si tenta
il ripristino del vecchio target; payload nuovi/parziali sono conservati in
ETUX-Backups, mai cancellati ricorsivamente dall'installer. Errori di permesso,
disco, file bloccati o rollback sono visibili: non dichiarare successo dopo un
fallimento. I test esercitano la conservazione dopo un errore prima della
sostituzione; interruzione del processo, crash, race ostili e guasti durante
rollback non sono una garanzia atomica provata. Escludere FreeCAD aperto e non
modificare manualmente i percorsi durante l'operazione.

## Link e rimozione

Installer: rifiuta reparse point (junction/symlink) negli antenati, nei payload,
nel target e nel suo contenuto. Rifiuta sorgente/destinazione annidate o coincidenti.
Non segue una Mod rediretta verso altre workbench. Un'installazione tramite link
va rimossa esplicitamente prima di installare una copia reale.

Uninstaller: solo leaf `ET-FreeCAD-UX` sotto Mod del profilo esplicito, identita
verificata, conferma, ricontrollo target. Directory reale senza link interni:
`Directory.Delete(target, true)`. Link/junction alla root di ET UX riconosciuta:
`Directory.Delete(target)` senza ricorsione, conservando la destinazione.
Link interrotti/estranei o contenuti con reparse point sono rifiutati.
Backup e altre workbench non sono toccati; assenza del target e idempotente.
I controlli sono precauzioni di deployment locale, non un sandbox contro un
processo ostile che cambia link/ACL fra verifica e operazione.

## Diagnostica host e privacy

`tools/diagnose_freecad.py` espone `run()` con dipendenze host iniettabili e
`save_report()` su scelta esplicita. `tools/diagnose_freecad.FCMacro` offre
esecuzione/salvataggio attraverso i dialoghi FreeCAD/PySide inclusi. Controlla
versione e binding effettivo, registrazione (senza mascherare loader falliti),
comandi, quattro schede, duplicati, due toggle e un cambio workbench, dimensioni/
visibilita toolbar standard e dock nativi. Ripristina workbench e flag opt-in
iniziali; nessun modello viene creato/modificato. Un task aperto produce `blocked`
prima di cambiare UI. FreeCAD 1.0 e secondario; `reference_113` distingue il target.

Il rapporto usa campi consentiti: software/versioni/sistema, comandi del catalogo,
conteggi/booleani e codici delle fasi. Non legge cronologia Report, preferenze,
percorsi utente, documenti, ambiente o contenuti CAD. Eccezioni senza testo o
traceback; etichette inattese non vengono esportate. Registrazione assente,
comandi mancanti e failure UI/ripristino rappresentano gli errori osservati;
non si certifica l'assenza di errori di altri addon o si raccolgono log grezzi.
Il JSON percorso installazione e distinto, privato ed escluso da Git/payload.

## Test e ambienti

`tests/windows/test-windows.ps1` usa cartelle temporanee nuove, source fixture
locale, profilo finto con spazi/Unicode e junction Windows. Non usa il vero Mod
dell'utente, non richiede Pester, non installa dipendenze o altera policy.
Esercita install/update/backup, legacy, processo aperto simulato, identity/failure,
WhatIf, rimozione idempotente e link. Eseguire dalla root:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\windows\test-windows.ps1
```

Il bridge unittest esegue la suite se PowerShell e presente, altrimenti segnala
uno skip esplicito. I test diagnostica fake verificano registration/task/errori
anonimi; il runner host esegue anche la diagnostica reale dopo lo smoke V0.3a.

La CI Windows usa checkout fissato a v4.2.2, PowerShell 5.1 e 7. Il job CAD CI
scarica **solo per i test** il portable ufficiale FreeCAD 1.1.3, verifica SHA256
`9c6959dc9c4dba64dd818a62447e3dfedb4221d776fb044b239d462f150bcec4` prima
dell'estrazione e usa il suo Python/Qt. Fonte: asset ufficiale
[FreeCAD_1.1.3-Windows-x86_64-py311.7z](https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.3),
ID `489303591`, digest API release controllato il 13 ottobre 2026. Nessun codice
remoto di bootstrap e nessun binding pip. Il downloader CI non fa parte degli
script di installazione utente.

`tools/windows/test-freecad113.ps1 -RuntimeRoot <portable estratto>` e un runner
dev per una copia gia locale: cerca runtime univoco, isola config/data/temp tramite
FREECAD_USER_HOME/DATA/TEMP (API ambiente host documentata nel sorgente 1.1.3),
usa il runner con versione esatta e ripristina l'ambiente del processo. Non richiede
che l'utente finale configuri queste variabili. Risultati e limiti aggiornati:
[VALIDATION_V03B.md](VALIDATION_V03B.md). GUI offscreen non equivale a desktop
Windows 10/11, loader completo, ergonomia/DPI/temi o policy aziendali.
