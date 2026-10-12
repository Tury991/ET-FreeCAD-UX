# Requisiti e matrice di riferimento

Il riferimento principale è **FreeCAD 1.1.3**, fissato esattamente per lo sviluppo V0.2. FreeCAD 1.0 è secondario e resta verificato sulla build disponibile; non deve limitare automaticamente le funzionalità di un addon opzionale Qt6.

| Componente | Requisito | Evidenza / stato |
| --- | --- | --- |
| ET UX core e test puri | Python >=3.8, libreria standard | 8 test unitari V0.2; eseguiti anche con Python 3.11.14 e 3.13.5 |
| Runtime principale | FreeCAD 1.1.3 Linux x86_64 ufficiale | AppImage verificata SHA256; Python 3.11.14, Qt/PySide6 6.8.3, OpenCASCADE 7.8.1 |
| Runtime secondario | FreeCAD 1.0.0 Debian | Python 3.13.5, Qt/PySide2 5.15.15, OpenCASCADE 7.8.1; 8 unitari, 8 geometrici e smoke GUI V0.2 passano |
| GUI ET UX | binding fornito dal runtime | nessun pacchetto Qt esterno obbligatorio; menu/toolbar standard |
| Bootstrap Linux cloud | bash, curl, sha256sum, x86_64 e spazio disco | circa 782 MiB download + 3.1 GiB estratti; profili temporanei in /tmp |
| GUI offscreen | plugin Qt offscreen incluso, cache/config/data XDG scrivibili | verificata; non richiede display o FUSE e non dimostra rendering CAD OpenGL |
| Nxt opzionale | minimi dichiarati FreeCAD 1.1.0, Python 3.11; Qt6 con QtQml/QtQuick/QtQuickWidgets | moduli importabili nell'AppImage 1.1.3; addon non eseguito. Qt5 di sistema non soddisfa questa implementazione |
| Ribbon opzionale | minimi dichiarati FreeCAD 0.21, Python 3.8; binding da verificare | addon non eseguito su 1.1.3; versione minima non è certificazione di compatibilità |

Non si aggiungono dipendenze pip alla workbench: né Ribbon né Nxt sono obbligatori. Le dipendenze dev di Nxt servono ai suoi test esterni, non sono istruzioni per sostituire PySide nel Python di FreeCAD.

Versioni, feature flag e build diverse da quelle in tabella richiedono nuove prove. Windows/macOS, scoperta completa dell'addon, DPI/temi, interazione desktop, QML Nxt e coesistenza Nxt+Ribbon+ET UX rimangono non verificati. Il pin 1.1.3 non equivale a una dichiarazione su ogni release 1.1.

Per riprodurre test e installazione: [guida cloud](FREECAD_113_CLOUD.md). Per decidere cosa riusare: [confronto estensioni](EXTENSIONS_COMPARISON.md).

Risultati Mechanical Workspace aggiornati: [VALIDATION_V02.md](VALIDATION_V02.md).
