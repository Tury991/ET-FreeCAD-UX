# V0.3a — fattibilità Ribbon e scelta del prototipo

Studio del 12 ottobre 2026 (Europe/Rome). Base prodotto: ultimo `main` remoto
`6a401f71760ac82b8371589cb9a58c15c95deb25` (merge V0.2). Il checkout cloud era
precedente; il proxy Git non rispondeva. I file V0.2 sono stati recuperati tramite
connettore GitHub al commit fissato, preservando il checkout esistente. Il commit
pubblicato usa direttamente questo SHA remoto come genitore; la materializzazione
locale della base non viene inclusa nella PR.

## FreeCAD-Ribbon: evidenze e limiti

Riesaminato [APEbbers/FreeCAD-Ribbon](https://github.com/APEbbers/FreeCAD-Ribbon)
al commit `b48a2c55d881d870ce98a5219e98afb0f5e3cce4`, ancora `main` al controllo
API. Lettura statica di README, LICENSE, package.xml, InitGui e FCBinding tramite
GitHub; nessun codice addon eseguito. Fonti e dettagli nel [precedente studio](FREECAD_RIBBON.md).

- **Licenza:** LICENSE/README GPL v3, package.xml GPL-3.0-or-later; header
  InitGui/FCBinding LGPL v3+. Incoerenza ancora presente: chiarire con upstream
  prima di incorporare/redistribuire codice, pacchetto locale PyQtRibbon o asset.
  La licenza ET UX è ancora da decidere. Non viene dichiarata compatibilità legale
  di una distribuzione combinata.
- **Architettura:** addon globale, startup InitGui, FCBinding ampio, dock Ribbon,
  event filter e callback workbenchActivated; renderer PyQtRibbon locale, layout
  JSON, editor, preferenze e stylesheet. Non emerge un contratto pubblico piccolo
  per montare/smontare un renderer ET UX indipendente con lifecycle circoscritto.
- **Compatibilità dichiarata:** versione 1.11.14, Python >=3.8, FreeCAD >=0.21;
  SearchBar, SaveAndRestore e `git` opzionali. Questi minimi non certificano
  FreeCAD 1.1.3/Qt6 o la build 1.0/Qt5. Non è stato fatto uno smoke addon.
- **Manutenzione:** `main` osservato include una correzione del colore testo con
  OpenTheme dark. La data 2024-07-28 del manifest è una data metadata, non prova
  di abbandono. Nella revisione studiata non è emersa una suite Python/CI test;
  non si deduce assenza di test manuali né un impegno di manutenzione futuro.
- **Rischi concreti:** README segnala ordine Assembly/Assembly4; dopo rimozione
  può servire ripristino toolbar con macro o SaveAndRestore. La portata globale
  contrasta con il requisito del prototipo locale e reversibile senza preferenze.

## Confronto

| Criterio | FreeCAD-Ribbon esterno opzionale | Prototipo Qt/PySide ET UX |
| --- | --- | --- |
| Funzioni | editor JSON, pannelli, layout ricchi e customizzazione | quattro schede fisse, due righe, scroll orizzontale |
| Riuso | configurazione di addon installato separatamente | catalogo e 24 QAction native V0.2; due azioni informative ET UX |
| Dipendenze | nessuna obbligatoria se resta esterno; versioni/schema da verificare | solo binding incluso nell'host, nessun pip |
| Ambito e stato | gestisce UI e preferenze globali | un QToolBar ET UX, stato in memoria, fallback V0.2 |
| Reversibilità | rimozione/ripristino upstream da testare | cleanup idempotente su toggle, cambio workbench, Close |
| Qt5/Qt6 | import e pacchetto locale da provare su entrambi | facade PySide, API Widgets comuni; eseguito su entrambi |
| Costo | evitare fork; coordinamento/schema/API upstream | piccolo renderer originale da mantenere; nessun editor generale |
| Licenza | GPL/LGPL da chiarire prima di incorporare | nessun codice/asset upstream; licenza ET UX ancora aperta |

**Raccomandazione:** per V0.3a adottare il piccolo prototipo Qt locale, opt-in e
standard come default. La motivazione verificabile è il controllo del lifecycle
e dello stato delle sole superfici ET UX. Non è una scelta di riscrivere editor,
framework Ribbon o tutte le funzionalità upstream. Il risultato resta sperimentale:
il costo di manutenzione Qt e il valore ergonomico vanno valutati sul desktop.

**Integrazione esterna possibile, ma non implementata/certificata:** l'addon
FreeCAD-Ribbon può essere installato separatamente e configurato per raccogliere
le toolbar native ET UX. Il prodotto funziona senza addon e non lo importa
all'avvio. Provare in profilo isolato e con pin; tenere il prototipo ET UX spento
durante la prova upstream per evitare due renderer. Un adapter automatico futuro
richiede capability checks, schema/API documentati e rollback verificato. Non
scrivere nei JSON utente né importare internamente FCBinding. Nessun componente
Ribbon o Nxt è stato copiato, installato o eseguito per questo prototipo.

## Rischi gestiti e prove ancora necessarie

- **Duplicazione:** Initialize costruisce toolbar/menu V0.2 una sola volta;
  activate è idempotente, deactivate rimuove il widget dalla finestra prima della
  cancellazione differita. Timer single-shot cancellato su disattivazione/chiusura.
  Cinque cicli toggle e cinque cambi più un cambio rapido sono testati.
- **Toolbar/preferences:** `hide()` sulle toolbar native è stato scartato: l'host
  può memorizzare la visibilità in fase di cambio. Il prototipo comprime min/max
  a zero, mantenendo invariati i flag di visibilità, e ripristina i limiti originali.
  Non usa ParamGet, saveState/restoreState o stylesheet globali. Posizionamento e
  stato salvato dall'host dopo riavvio rimangono un gate desktop; crash/kill non
  consentono cleanup Python e non sono una reversibilità certificata.
- **Workbench/task:** nessuna toolbar esterna viene compressa, nessun cambio
  forzato; Sketcher può cambiare workbench nativamente. Tree, proprietà, task,
  selezione e transazioni restano host. Nessun riferimento persistente a documenti.
  Coesistenza con Ribbon/Nxt/Assembly4 non testata.
- **Temi:** icone/testo/abilitazione sono quelli delle QAction; palette e font
  ereditati, niente colori rigidi o branding proprietario. Temi scuri, contrasto,
  font grandi, DPI e accessibilità da verificare realmente; altezza 116 px Qt
  è una scelta compatta sperimentale, non una validazione ergonomica.
- **Qt5/Qt6:** non importare QAction da un namespace fisso né scegliere binding
  in base al solo numero FreeCAD. Il facade PySide dell'host fornisce QtWidgets
  e QtCore; nessun QtQuick richiesto. Binding assente o superficie incompleta
  produce diagnosi e fallback; nessuna patch host.
- **Layout:** le schede scorrono orizzontalmente se i pulsanti non entrano; la
  Ribbon è ancorata in alto e non flottante. Resize a 480 px esercitato offscreen;
  resa visiva, eventuali spazi delle toolbar compresse e flussi tastiera richiedono
  una prova desktop. Non sono implementati editor, shortcut o schede contestuali.

Attivazione/disattivazione nel [README](../README.md). Esiti e perimetro dei test
nel [rapporto V0.3a](VALIDATION_V03A.md). Nessuno screenshot è incluso; nessuna
esperienza grafica interattiva è dichiarata verificata.
