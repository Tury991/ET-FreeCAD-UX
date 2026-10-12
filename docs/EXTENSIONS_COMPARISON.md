# Strategia tecnica pre-V0.2: ET UX, Ribbon e Nxt

Decisione del **12 ottobre 2026**. FreeCAD **1.1.3** è il riferimento principale verificato nel cloud; **1.0** resta una regressione secondaria per ET UX. Le estensioni opzionali non devono essere abilitate sulla base del solo numero di versione.

## Confronto architetturale

| Aspetto | ET UX V0.1 | FreeCAD-Ribbon | FreeCAD-Nxt |
| --- | --- | --- | --- |
| Scopo | base per guida del workflow | renderer ribbon e editor layout | model panel, proprietà e interazioni dirette |
| Tipo | workbench Python locale | addon che modifica la presentazione globale | addon globale, senza workbench propria |
| Architettura | catalogo puro → adapter → menu/toolbar | `InitGui`, ampio `FCBinding`, dialoghi, JSON e pacchetto PyQtRibbon locale | package `freecad.nxt`, app/services, core, tree, inspector, menus, tools, QML e bridge |
| Lifecycle | Initialize idempotente; nessun servizio globale | startup e workbenchActivated, dock/event filter, migrazioni/preferenze | startup differito, workbench manipulator, servizi di sessione e cleanup |
| Configurazione | nessuna preferenza persistente iniziale | JSON layout, namespace Ribbon e stato finestra | preferenze, TOML menu/template, defaults gizmo e backend scenegraph |
| Qt | nessun import Qt nel prodotto iniziale | PySide e codice condizionale PySide6; binding da verificare | QtWidgets facade + QtQuick direttamente PySide6 |
| Minimi dichiarati | core Python >=3.8, target host 1.1.3 | FreeCAD >=0.21, Python >=3.8 | FreeCAD >=1.1.0, Python >=3.11, Qt6/QtQuick effettivi |
| Test osservati | 4 unitari invariati + 4 geometrici + smoke host, eseguiti | nessuna suite Python/CI test emersa nella revisione letta | test fake host e QML, CI lint/tipi/offscreen letta; non rieseguita |
| Licenza | ancora da definire | GPL v3 / GPL-3.0-or-later nei metadati; header LGPL incongruenti | LGPL-2.1-or-later nei metadati, testo LGPL 2.1 |
| Stato compatibilità 1.1.3 | test ET UX passati con Qt6 | analisi statica, non runtime | QtQuick disponibile, addon non eseguito |
| Stato compatibilità 1.0 disponibile | test ET UX passati con Qt5 | analisi statica, non runtime | minimi non soddisfatti: build 1.0 Qt5 priva di PySide6 |

Le revisioni sono fissate negli [studi Ribbon](FREECAD_RIBBON.md) e [Nxt](FREECAD_NXT.md). Le architetture sono complementari per ambito, ma **la coesistenza non è provata**: Ribbon/Nxt intervengono entrambi su finestre, eventi, preferenze e interazione.

## Cosa riusare prima di costruire

| Bisogno | Disponibilità esistente | Strategia ET UX |
| --- | --- | --- |
| ribbon, dimensioni pulsanti, pannelli configurabili | Ribbon JSON e editor | provare addon/configurazione esterna; niente renderer ribbon completo ora |
| tree/timeline, relazioni, rollback | tree standard e Nxt model panel | non implementare un FeatureManager parallelo; valutare Nxt opzionale |
| inspector di proprietà | editor/task panel FreeCAD e Nxt inspector | riusare comandi nativi; offrire il comando Nxt se verificato |
| gizmo, input flottanti, isolate, placement | FreeCAD e Nxt tools | non duplicare; testare il comando disponibile e la sua reversibilità |
| menu contestuali e condizioni generiche | Nxt TOML/definitions/facts/runner | non creare un secondo DSL; limitare le regole ET UX ai prerequisiti del percorso guidato |
| ricerca dei comandi | SearchBar menzionato come addon opzionale Ribbon | valutarlo prima di creare una nuova ricerca |
| riparazione sketch e attachment | solver/comandi nativi e Nxt repair/attach | non introdurre auto-repair ET UX; documentare modifiche al modello e Undo/Redo prima del riuso |
| percorso documento → Body → sketch → vincoli → feature | fondamenti Sketcher/PartDesign, azioni distribuite | contributo specifico ET UX: guida esplicita, prerequisiti leggibili e meno cambi di workbench |

La guida del percorso ET UX può giustificare un piccolo modello di contesto puro: non equivale a riscrivere tree, inspector o motore di menu. Prima di aggiungere una funzione, documentare il comando/modulo esistente valutato, il bisogno che non copre e come si verificherà il valore aggiunto. Se non emerge un divario concreto, scegliere riuso o contributo upstream.

## Scelta tecnica

1. **ET UX autonomo e minimale** per la sequenza di lavoro, con comandi nativi e renderer standard funzionante anche senza addon.
2. **Nxt opzionale**, inizialmente tramite comandi registrati verificati. Non importare servizi/modelli/bridge privati come se fossero una libreria stabile. Richiedere capability checks e un pin dell'addon; non tentare di farlo funzionare su un host Qt5 aggiungendo pip Qt6.
3. **Ribbon opzionale** per la presentazione. Provare prima configurazione supportata, poi un contratto d'estensione upstream. Evitare un fork permanente o la copia del pacchetto locale.
4. **Nessuna integrazione attivata adesso**: questa PR aggiorna strategia, requisiti e test del runtime. Non modifica il motore, non copia codice upstream e non aumenta la versione prodotto a 0.2.

## Licenze e compatibilità di distribuzione

L'invocazione di un addon installato separatamente e l'incorporazione di suo codice sono forme di riuso diverse, da valutare nella distribuzione concreta. LGPL non significa assenza di obblighi; GPL non impedisce di usare l'addon, ma il riuso di codice in un derivato richiede una licenza compatibile e rispetto delle condizioni. Non è stata stabilita una licenza ET UX, quindi non si dichiara oggi compatibilità legale di una distribuzione combinata.

Per Nxt verificare attribuzioni e licenze dei file/asset riusati. Per Ribbon chiarire prima la differenza tra LICENSE/metadata GPL e header LGPL. Senza questi passi non incorporare moduli, QML, icone o stylesheet. Questa modifica contiene solo analisi e codice di test scritto per ET UX.

## Prossime prove prima delle integrazioni

- Profilo FreeCAD dedicato e revisioni addon fissate; prima ET UX da solo, poi Nxt o Ribbon singolarmente e infine la combinazione.
- Loader completo da Mod, selezione e cambio documento, task aperto, Undo/Redo, scorciatoie, temi/DPI e rimozione/restart con ripristino dello stato.
- QML/QtQuick: import, creazione della superficie e interazione reale. L'offscreen dei menu ET UX non certifica viewport OpenGL o gizmo Nxt.
- Fallback senza addon, comando assente e versioni incompatibili. Se l'integrazione richiede patch private o gestione globale fragile, mantenere la UI standard e proporre un punto d'estensione upstream.

Questi gate restano nella [roadmap](ROADMAP.md). Non vanno convertiti in dichiarazioni di compatibilità finché non sono stati eseguiti.
