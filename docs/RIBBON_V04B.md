# Ribbon V0.4b — Classic & Compact Modern

Implementazione locale opzionale richiesta, basata sullo [studio V0.4a](UX_V04A.md).
Base `main`: `d71d51889a8320e3632983e42ce343c4d155037b`, verificata via API GitHub
il 15 ottobre 2026. Nessun codice, icona o stylesheet Ribbon/Nxt/SolidWorks copiato.
Il renderer minimo ET UX già presente è esteso per densità e gruppi; non introduce
editor di layout, nuovi strumenti CAD, tree o task alternativi. Questa scelta
risponde alla richiesta e ai criteri di riuso di [EXTENSIONS_COMPARISON](EXTENSIONS_COMPARISON.md).

## Utilizzo

1. Seleziona ET FreeCAD UX e usa **ET UX → Ribbon sperimentale → Attiva/disattiva
   Ribbon sperimentale**. La prima densità è **Classic Modern**.
2. Nello stesso menu scegli **Classic Modern** o **Compact Modern**, oppure apri
   **Ribbon** nell'angolo della fascia. L'aggiornamento avviene sui widget esistenti:
   azioni, scheda selezionata e task nativi restano gli stessi.
3. **Ribbon → Toolbar standard**, oppure il toggle nel menu ET UX, ripristina le
   toolbar standard. Al riavvio l'interfaccia parte standard; la densità è ricordata.

La preferenza è `RibbonDensity` (`classic`/`compact`) in
`User parameter:BaseApp/Preferences/Mod/ETFreeCADUX`. Valori sconosciuti ricadono
su Classic; nessun tema, navigazione, shortcut o preferenza di altre workbench
viene scritto. Per tornare al valore iniziale basta scegliere Classic.
Per installazione, aggiornamento V0.3b con backup e rollback: [guida Windows](WINDOWS_GUIDE.md).

## Struttura e limiti

| Scheda | Gruppi, in ordine comune alle due densità |
| --- | --- |
| Features | Struttura: Body; Volume: Pad, Pocket, Revolution; Finitura: Fillet, Chamfer |
| Sketch | Sessione: Nuovo, Modifica, Chiudi; Geometria: Rettangolo, Cerchio; Quote e vincoli: Distanza, Raggio |
| Reference | Piano, Linea, Punto, Sistema di coordinate, SubShapeBinder |
| Tools | Documento; Cronologia; Strumenti; Supporto |

Il catalogo nativo e le toolbar/menu preesistenti restano invariati. Il renderer
ha un'unica mappa immutabile in `core/ribbon.py` e filtra le azioni disponibili;
le QAction originali sono risolte dall'adapter, senza proxy o modifica del dispatch.
Etichette, tooltip, icone, stato, selezione, conferme e transazioni restano nativi.
Nessuna modifica alla transizione Sketcher/ritorno ET UX già accettata.

Classic usa icone principali 40 DIP e secondarie 24; Compact 32 e 20. Minimi
pulsanti 44/32 DIP, spaziature 10/4, padding 8/4. La fascia riserva almeno
152/96 DIP per comandi, oltre a schede e scrollbar; metriche font e contenuti
possono richiedere più altezza. Qt gestisce i DPI: niente moltiplicatori manuali.

La palette e il font della main window vengono riportati **solo** nei widget
ET UX: alcuni contenitori Qt/FreeCAD hanno palette esplicite che interrompono
l'ereditarietà. Un filtro posseduto dal controller aggiorna palette/font al cambio
host ed è rimosso su disattivazione. Lo stylesheet è limitato al sottoalbero
`ETUX_RibbonSurface`: scheda attiva in grassetto e sottolineata, separatori,
hover e contorno focus. Stati disabilitati usano la palette nativa. Nessuna
scrittura di stile sulla main window, viewport, albero o pannelli Task.

In caso di overflow ogni scheda ha scorrimento orizzontale, senza riordinare o
eliminare comandi. un filtro di focus locale porta nel viewport i controlli raggiunti con Tab; le frecce
muovono le schede e il menu Ribbon offre le densità e il ritorno standard.
Il menu ET UX resta un accesso completo. Altezza calcolata sui contenuti, non
fissata. La verifica dei temi desktop e del contrasto delle icone native resta
necessaria: ET UX non sostituisce le risorse dell'host.

Su disattivazione vengono cancellati timer, filtri finestra/focus e riferimenti a widget/menu;
la toolbar ET UX viene rimossa e distrutta con `deleteLater`. Cleanup idempotente.
I limiti min/max delle sole toolbar ET UX vengono ripristinati, senza scriverne
la visibilità né toccare quelle di altre workbench. La densità può cambiare anche
con Ribbon spenta, senza importare Qt; errori renderer causano fallback standard.

## Differenze dai mockup

- Icone e nomi tradotti nativi, comprese etichette come “Revolve”: le icone blu
  geometriche dei concept erano segnaposto e non sono usate nel prodotto.
- Reference resta nella propria scheda; niente duplicazione “Piani/assi” in Features,
  menu Quota aggregato, accessi viste o “Altri comandi” aggiuntivi. Tutte le azioni
  verificate sono pulsanti espliciti, con menu ET UX sempre disponibile.
- Il menu angolare Ribbon raggruppa densità e Toolbar standard. Nessun redesign
  di albero/task/viewport; forme delle schede e colori seguono stile/palette host.
- I gruppi non collassano in menu al resize: lo scroll è un comportamento unico
  prevedibile. I font grandi possono ridurre il risparmio verticale Compact.

## Verifica

Esiti e catture reali offscreen in [VALIDATION_V04B](VALIDATION_V04B.md).
Le tavole [V0.4a](design/v0.4a/README.md) restano **mockup**, non screenshot.
