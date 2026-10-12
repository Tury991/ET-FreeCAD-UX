# Roadmap di sviluppo

Milestone ordinate per dipendenze, senza scadenze artificiali. Ogni fase richiede una demo e i propri criteri di accettazione prima di passare alla successiva.

| Fase | Ambito | Criteri di accettazione |
| --- | --- | --- |
| M0 — base, presente | loader Python, menu/toolbar standard, comando informativo, documenti e test | Su 1.1.3 e 1.0 passano 4 unitari originali, 4 geometrici e smoke GUI offscreen; la workbench non modifica documenti o preferenze; i test geometrici usano documenti temporanei. Restano da verificare installazione completa e desktop |
| M1 — compatibilità e distribuzione | riferimento 1.1.3, regressione secondaria 1.0, loader reale da Mod, matrice desktop Linux/Windows/macOS, licenza, package.xml e CI dei test puri | installazione/rimozione/riavvio dimostrati; versioni supportate dichiarate sulla base dei risultati; licenza e metadati approvati prima della distribuzione |
| M2 — workflow pezzo minimo | catalogo di azioni native, contesto documento/Body/selezione/modifica, percorso nuovo documento → Body → sketch → Pad | regole pure testate per documenti assenti, selezioni non valide e task aperti; demo desktop con FCStd riaperto e Undo/Redo; nessun comando geometrico reimplementato |
| M3 — organizzazione per attività | gruppi Sketch, Features, View e messaggi sui prerequisiti; valutare SearchBar prima di creare una ricerca | azioni coerenti col contesto e accessibili da tastiera; nessuna duplicazione dopo cambi documento/workbench; task panel nativi preservati |
| M4 — esperimento Ribbon opzionale | confronto UI standard/Ribbon e comandi Nxt opzionali, profilo separato e contributi upstream; nessun tree/inspector/gizmo duplicato | chiarite licenze e API/versioni; stessa demo M2 con/senza addon; disattivazione e rimozione ripristinano lo stato; nessuna dipendenza obbligatoria |
| M5 — qualità UX | preferenze opt-in, shortcut configurabili, traduzioni, DPI/temi, onboarding del workflow | test desktop su matrice supportata; nessuna scorciatoia sovrascritta silenziosamente; preferenze versionate e ripristino verificato |
| M6 — altri domini | assiemi, TechDraw e altri workflow tramite adapter distinti | prerequisiti e modello di ogni dominio documentati, selezione delle implementazioni supportate e test dedicati; nessuna promessa di equivalenza universale SolidWorks |

## Esperimento Ribbon: criterio di scelta

Prima provare configurazione esterna di FreeCAD-Ribbon, poi un adapter solo se offre un punto di integrazione stabile. Preferire una proposta upstream a un fork permanente. Se la compatibilità richiede patch interne, gestione globale della finestra o dipendenze difficili da testare, mantenere la UI standard e valutare un renderer minimale indipendente. Non riscrivere un'intera ribbon in M0–M3.

## Fuori dal perimetro iniziale

Modifiche al kernel FreeCAD, formati proprietari SolidWorks, clonazione completa della UI, solver aggiuntivi, tree view sostitutivo, import massivo di workbench, monkey patch e installazioni automatiche di addon. Misurare in M2–M3 numero di cambi workbench, errori sui prerequisiti e completamento del percorso da parte di utenti reali; un cambio estetico da solo non dimostra un workflow migliore.

## Gate pre-V0.2: strategia aggiornata

Il runtime ufficiale 1.1.3 è installato affiancato a 1.0, con checksum verificato e test riproducibili. Il riferimento 1.1.3 è un pin deliberato anche se esiste il tag 1.1.4: aggiornamenti successivi richiedono una verifica separata. [Requisiti](REQUIREMENTS.md), [studio Nxt](FREECAD_NXT.md) e [confronto](EXTENSIONS_COMPARISON.md) definiscono i confini prima di M2. Non aumentare ancora la versione prodotto a 0.2: questa modifica prepara la strategia e l’infrastruttura di test.
