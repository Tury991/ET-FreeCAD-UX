# Windows 10/11 — installare e provare ET FreeCAD UX V0.3b

Serve FreeCAD **1.1.3** gia installato. Non servono Python separato, Qt, pip, Git
o privilegi amministrativi per la workbench. La Ribbon resta sperimentale.
I test Linux offscreen non certificano il collaudo desktop Windows; annota gli
esiti della procedura qui sotto sulla tua macchina.

## Installazione dalla copia scaricata

1. Scarica lo ZIP del branch `feature/windows-first-v0.3b` dalla pagina GitHub
   del progetto (Code → Download ZIP) ed estrailo con Esplora file. Non eseguire
   comandi che scaricano ed eseguono script dalla rete. Apri la cartella che contiene
   **InitGui.py, install-windows.ps1, uninstall-windows.ps1 ed etux-package.json**.
2. Avvia il FreeCAD 1.1.3/profilo che usi normalmente. Con **File → Apri** apri
   `tools/export_user_directory.FCMacro` della copia estratta. Nell'editor della
   macro usa **Macro → Esegui macro** (F6). Salva `freecad-user-path.json` nella
   stessa cartella di `install-windows.ps1`. Se il dialogo propone un'altra cartella,
   scegli quella estratta. La macro usa `App.getUserAppDataDir()` del FreeCAD reale,
   quindi funziona anche con un profilo o una directory personalizzati.
3. Il JSON contiene un percorso personale: conservalo localmente, non allegarlo
   a segnalazioni. Chiudi **tutti** i processi FreeCAD, incluso FreeCADCmd.
4. Apri la cartella estratta in Esplora file, scrivi `powershell` nella barra
   dell'indirizzo e premi Invio. Si apre Windows PowerShell senza amministratore.
   Esegui esattamente:

   ```powershell
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\install-windows.ps1" -UserDataFile ".\freecad-user-path.json"
   ```

   Controlla la destinazione mostrata (`<directory del profilo>/Mod/ET-FreeCAD-UX`)
   e conferma con **Y/S**, secondo la lingua della richiesta PowerShell. Se non
   corrisponde al profilo voluto, rispondi No e riesegui la macro in quel profilo.
   `-ExecutionPolicy Bypass` vale solo per questo processo; non cambia la policy
   di sistema o dell'utente. Esegui soltanto la copia locale del progetto che hai
   controllato. Una policy aziendale puo bloccarlo: non tentare di modificarla.
5. Riavvia FreeCAD. Nel selettore delle workbench scegli **ET FreeCAD UX**.
   Apri **Visualizza → Pannelli → Report** per leggere eventuali errori localmente.
   Devono esserci il menu **ET UX** e i gruppi Sketch, Features, Reference e Tools.
   Non devi configurare interpreti, variabili Python o binding Qt.

Le virgolette proteggono spazi/Unicode nei percorsi. In alternativa, il percorso
assoluto ottenuto dalla Console Python di FreeCAD con
`print(App.getUserAppDataDir())` si puo passare a `-FreeCADUserDir`, al posto di
`-UserDataFile`. Lo script non sceglie automaticamente un profilo da APPDATA.
Un file percorso vecchio si riferisce al vecchio profilo: rigenera il JSON dopo
aver cambiato profilo/versione portable. La macro non modifica preferenze.

Per un'anteprima senza scritture aggiungi `-WhatIf` al comando. Non usare
`-Confirm:$false` nel collaudo manuale: lascia visibile la conferma.

## Primo avvio e Ribbon

Seleziona **ET FreeCAD UX**, poi **ET UX → Ribbon sperimentale →
Attiva/disattiva Ribbon sperimentale**. Devono comparire quattro schede:
**Sketch, Features, Reference, Tools**. Albero delle feature, proprieta e task
rimangono quelli di FreeCAD. Il pulsante **Toolbar standard** disattiva la Ribbon.
All'avvio successivo il default e standard; l'opt-in dura soltanto nella sessione.

Se un comando e grigio, verifica i prerequisiti nativi: documento, Body attivo,
sketch o spigoli selezionati e assenza di un task da concludere. La Ribbon non
abilita forzatamente comandi non eseguibili.

## Collaudo di un pezzo parametrico

Usa un documento di prova nuovo, non un modello di lavoro.

1. In **Tools** crea un documento. In **Features** crea un **Body**. Verifica
   nell'albero che sia attivo; con piu Body attiva quello voluto con doppio clic.
2. In **Sketch** scegli **Nuovo sketch**, seleziona **piano XY** nel task e conferma.
   FreeCAD puo passare a Sketcher: e il comportamento nativo, non un errore.
3. Disegna un cerchio centrato sull'origine. Seleziona il cerchio e imposta un
   vincolo di **raggio 5 mm**. Chiudi lo sketch dal task/Sketcher e torna a ET UX.
4. Seleziona lo sketch nell'albero. In **Features → Pad**, imposta **10 mm** e
   conferma nel task nativo. Il volume senza altre feature e circa **785,398 mm3**.
5. Modifica lo sketch con doppio clic oppure **Modifica sketch**. Cambia il
   vincolo di raggio a **7 mm**, chiudi e ricalcola da Tools. Il Pad deve aggiornarsi:
   volume circa **1539,380 mm3**. Prova Undo/Redo e modifica anche la lunghezza Pad
   nel pannello proprieta; ripristina 10 mm prima delle prove seguenti.
6. Seleziona la faccia superiore del Pad, crea un secondo sketch con un cerchio
   di raggio **2 mm** interno al primo profilo. Chiudi, seleziona lo sketch e usa
   **Pocket**, profondita **3 mm**. Conferma: deve apparire una cavita nel Body.
7. Seleziona uno spigolo esterno valido e prova **Fillet**, raggio piccolo (per
   esempio **1 mm**). Conferma oppure annulla il task se la geometria non lo
   permette. Su un altro spigolo adatto prova **Chamfer**, per esempio **0,5 mm**.
   Concludi ogni task prima del successivo; non serve che qualsiasi spigolo
   accetti qualsiasi valore. Errori e anteprime rimangono nativi.
8. Alterna **ET FreeCAD UX** e **Part Design** almeno tre volte, senza task aperti.
   Tornando a ET UX la Ribbon si ricrea una sola volta. Disattivala: deve restare
   una sola toolbar per gruppo e le toolbar Part Design non devono essere alterate.
9. Salva un **FCStd**, chiudi il documento e riaprilo con File → Apri. Verifica
   albero, Body, sketch/vincoli e Pad/Pocket/Fillet/Chamfer creati. Modifica una
   quota, ricalcola e prova Undo/Redo. Non includere questo file nei log diagnostici.
10. Premi **Toolbar standard** o usa di nuovo il toggle. Verifica menu e toolbar
    V0.2, albero e proprieta. Chiudi e riapri FreeCAD: deve partire con UI standard.

Annota separatamente eventuali problemi di finestra stretta, tema scuro/chiaro,
scala Windows 100/150/200%, navigazione tastiera, task, salvataggio e riapertura.
L'offscreen Linux non sostituisce queste osservazioni.

## Aggiornare e tornare alla versione precedente

Estrai la nuova copia in una **cartella separata**, riesegui la macro percorso
se necessario, chiudi FreeCAD e ripeti il comando di installazione dalla nuova
cartella. La vecchia installazione viene spostata integralmente in
`<directory del profilo>/ETUX-Backups/ET-FreeCAD-UX-<data>-<id>`; non viene mescolata
con la nuova e il backup non si trova in Mod. Il percorso del backup appare alla fine.
Le installazioni originali V0.1/V0.2/V0.3a sono riconosciute tramite file/hash noti;
copie modificate non riconosciute sono rifiutate senza sovrascriverle.

Per rollback chiudi FreeCAD, disinstalla la copia corrente con il comando sotto
e poi, in Esplora file, **copia** la cartella del backup desiderato in
`<directory del profilo>/Mod/ET-FreeCAD-UX`. Non unire cartelle e non rinominare
altre workbench. Conserva il backup originale e riavvia FreeCAD.

## Disinstallare

Chiudi FreeCAD. Dalla cartella scaricata che conserva script e JSON privato:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\uninstall-windows.ps1" -UserDataFile ".\freecad-user-path.json"
```

Controlla il percorso e conferma. Viene rimossa solo **ET-FreeCAD-UX** in quel
profilo; backup, documenti, preferenze e altre workbench restano. `-WhatIf` mostra
la rimozione senza eseguirla. Una junction/link alla root di un pacchetto ET UX
riconosciuto viene eliminata **senza eliminare la destinazione**. Link interni,
Mod tramite junction, link interrotti o directory estranee sono rifiutati:
non tentare una cancellazione ricorsiva manuale per aggirare l'errore.

## Rapporto diagnostico senza dati personali

1. Con FreeCAD aperto, concludi/annulla eventuali task. Non serve chiudere documenti:
   la diagnostica non li modifica. Apri `tools/diagnose_freecad.FCMacro` con
   File → Apri e usa Macro → Esegui macro/F6. Puoi usare la copia estratta oppure
   quella installata. Se richiesto, seleziona il file locale `tools/diagnose_freecad.py`.
2. Salva il rapporto come `etux-diagnostic.json` dove preferisci. Lo strumento
   controlla versione/binding, registrazione reale, 24 comandi, schede Ribbon,
   toggle, duplicati, cambio workbench e ripristino. Ripristina la workbench e
   l'opt-in iniziali; non registra manualmente una workbench che ha fallito il loader.
3. Esito **pass**: controlli automatici riusciti, non certificazione della grafica.
   **blocked**: c'e un task aperto, concludilo e ripeti. **fail**: conserva il JSON
   e indica quale passaggio della guida non funziona, senza nomi/percorso del modello.
4. Apri il JSON con Blocco note e controllalo prima di inviarlo. Contiene solo
   versioni software, sistema operativo, ID comandi, conteggi, flag ed errori
   codificati. Non include utenti, percorsi, nomi documento, geometria, variabili
   d'ambiente, testo delle eccezioni o cronologia del pannello Report.
   **Non allegare** `freecad-user-path.json`, file FCStd, log completi FreeCAD,
   transcript PowerShell o screenshot contenenti dati personali.

Il rapporto identifica i fallimenti osservabili (registrazione assente, comandi
mancanti, errori nella UI/ripristino); non legge tutta la cronologia di errori di
altri addon. Se la macro non si avvia, controlla localmente il pannello Report e
la completezza della copia. Non installare un binding Qt esterno per correggerlo.
