# Studio FreeCAD-Ribbon e decisione iniziale

## Fonti e metodo

Analisi statica effettuata il **12 ottobre 2026** sul repository [APEbbers/FreeCAD-Ribbon](https://github.com/APEbbers/FreeCAD-Ribbon), branch `main`, commit **b48a2c55d881d870ce98a5219e98afb0f5e3cce4**. È la variante indicata dal catalogo ufficiale [FreeCAD-addons](https://github.com/FreeCAD/FreeCAD-addons/blob/9dbf44fbbc7f0260aa07b21468914e531a979416/.gitmodules). Il README riconosce come predecessori Geolta/FreeCAD-Ribbon e HakanSeven12/Modern-UI: non vanno confusi con la variante qui esaminata.

Le fonti sono state lette da un clone temporaneo esterno al progetto. Ribbon non è stato installato o eseguito, né copiato nel prodotto. L'API di ricerca GitHub era bloccata dal proxy; il catalogo ufficiale e l'accesso Git HTTPS hanno consentito di individuare e leggere il repository. Le conclusioni di runtime sono quindi ipotesi da verificare con M4, non risultati di compatibilità certificata.

Fonti fissate al commit analizzato:

- [README](https://github.com/APEbbers/FreeCAD-Ribbon/blob/b48a2c55d881d870ce98a5219e98afb0f5e3cce4/README.md): funzionalità, installazione/rimozione e problemi noti.
- [package.xml](https://github.com/APEbbers/FreeCAD-Ribbon/blob/b48a2c55d881d870ce98a5219e98afb0f5e3cce4/package.xml): versione dichiarata 1.11.14, Python minimo 3.8, FreeCAD minimo 0.21, addon SearchBar/SaveAndRestore e modulo `git` opzionali. La data nei metadati è 2024-07-28; non coincide con l'ultimo commit e non dimostra da sola lo stato di manutenzione.
- [InitGui.py](https://github.com/APEbbers/FreeCAD-Ribbon/blob/b48a2c55d881d870ce98a5219e98afb0f5e3cce4/InitGui.py) e [FCBinding.py](https://github.com/APEbbers/FreeCAD-Ribbon/blob/b48a2c55d881d870ce98a5219e98afb0f5e3cce4/FCBinding.py): startup, connessioni GUI, presentazione e stato.
- [RibbonUI.py](https://github.com/APEbbers/FreeCAD-Ribbon/blob/b48a2c55d881d870ce98a5219e98afb0f5e3cce4/RibbonUI.py), [Parameters_Ribbon.py](https://github.com/APEbbers/FreeCAD-Ribbon/blob/b48a2c55d881d870ce98a5219e98afb0f5e3cce4/Parameters_Ribbon.py) e [pacchetto locale](https://github.com/APEbbers/FreeCAD-Ribbon/tree/b48a2c55d881d870ce98a5219e98afb0f5e3cce4/Resources/packages/pyqtribbon_local).
- [LICENSE](https://github.com/APEbbers/FreeCAD-Ribbon/blob/b48a2c55d881d870ce98a5219e98afb0f5e3cce4/LICENSE): testo GPL v3.

## Cosa offre e come funziona

Ribbon sostituisce le toolbar standard con categorie/pannelli basati sui comandi delle workbench. Salva il design in JSON e offre un editor per dimensioni dei pulsanti, ordine, esclusione di workbench e toolbar, combinazione di pannelli e comandi provenienti da workbench diverse. Riutilizza il lavoro Modern-UI e una variante locale di PyQtRibbon: non è semplicemente una dipendenza pip intercambiabile.

`InitGui.py` importa API FreeCAD e PySide, modifica proprietà della finestra secondo preferenze, migra file di configurazione e collega `workbenchActivated` a `FCBinding.run`. `FCBinding.py` contiene oltre 7.600 righe e importa dialoghi, serializzazione, cache, widget e impostazioni. La classe `run` costruisce la ribbon in un `QDockWidget`; altre parti installano event filter e gestiscono menu, stile e stato. `RibbonUI.py` registra comandi aggiuntivi e usa un controllo di import PySide6 per alcuni di essi. Questo rende rilevante il test del binding Qt concreto, non soltanto il numero di versione FreeCAD.

Il README descrive il ripristino delle toolbar dopo disinstallazione e un conflitto di ordine tra Assembly nativa e Assembly4. Sono segnali concreti della portata globale del componente. La workbench ET UX iniziale usa invece soltanto le API standard per i propri menu e toolbar.

Nel checkout analizzato non sono emerse suite Python di test o workflow CI di test; `.github` contiene template di issue. Questa osservazione non significa che upstream non faccia verifiche manuali. Il commit più recente esaminato corregge il colore del testo con OpenTheme dark, quindi non vi sono elementi per definirlo abbandonato.

## Licenza e riuso

README e LICENSE indicano GPL v3; `package.xml` indica `GPL-3.0-or-later`, mentre intestazioni di file come `InitGui.py` e `FCBinding.py` parlano di LGPL v3 o successiva. Prima di copiare, modificare o redistribuire codice occorre chiarire con upstream questa incoerenza e le licenze del pacchetto locale e degli asset. Non presumere una licenza permissiva dalla sola libreria PyQtRibbon. Anche un'integrazione distribuita deve essere valutata nella sua forma concreta. ET UX non incorpora codice upstream in questa fase; la propria licenza resta da definire.

## Confronto delle opzioni

| Opzione | Vantaggi | Costi e vincoli | Valutazione iniziale |
| --- | --- | --- | --- |
| Integrare come addon esterno opzionale, prima tramite configurazione | UI già ricca, editor JSON, manutenzione condivisa | stato globale e coesistenza da testare; compatibilità dello schema e delle versioni; nessuna API ET UX garantita dall'analisi | migliore candidato a un esperimento M4 |
| Estendere upstream | evita duplicazione del renderer; può introdurre un contratto stabile per gruppi contestuali | richiede accordo upstream, isolamento del lifecycle e chiarimento licenze | preferibile a un fork se il prototipo dimostra una necessità reale |
| Fork o incorporazione diretta | controllo completo del comportamento | manutenzione di GUI/Qt, migrazioni e asset; accoppiamento forte e obblighi di licenza | sconsigliato per la base iniziale |
| Workbench autonoma con menu/toolbar standard | dipendenze minime, test senza host, minore superficie di compatibilità | non dà subito l'aspetto ribbon; renderer avanzato eventualmente da costruire | scelta attuale per M0–M3 |

## Decisione

**Costruire ora il workflow indipendente; valutare poi Ribbon come presentazione opzionale.** Non sviluppare subito una ribbon alternativa completa. L'obiettivo è ridurre attriti nel percorso di modellazione, che un renderer Ribbon non risolve da solo. Catalogo e regole del workflow devono restare indipendenti sia da Qt sia dall'addon.

Per il successivo esperimento:

1. Usare un profilo FreeCAD separato e salvare le preferenze di prova; installare una revisione Ribbon identificata.
2. Verificare se i comandi `ETUX_` e le toolbar della nuova workbench sono raccolti senza modifiche upstream, e se una configurazione esterna basta. Non scrivere direttamente nei JSON utente senza un metodo supportato.
3. Ripetere la demo pezzo, cambi workbench/documento, task di modifica aperto, temi/DPI e disattivazione/rimozione su Qt5 e Qt6 e sui sistemi dichiarati supportati.
4. Se occorre un adapter, concordare un contratto versionato e un punto di estensione upstream. Gestire addon assente/versione incompatibile con fallback standard, senza import globali di `FCBinding`.
5. Chiarire licenze prima di distribuire derivazioni. Se non esiste un'integrazione stabile o reversibile, mantenere la UI standard e prototipare un renderer piccolo e circoscritto.

La decisione è rivedibile dopo questi risultati. Non è dimostrato che Ribbon sia incompatibile con ET UX, né che l'integrazione funzioni già.
