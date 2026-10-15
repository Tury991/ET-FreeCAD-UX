# Catture reali della Ribbon V0.4b — Linux offscreen

Questi PNG sono catture **reali di widget FreeCAD 1.1.3/Qt6**, ottenute con
`QToolBar.grab()` durante lo smoke; non sono mockup e non sono screenshot del
desktop Windows. Mostrano soltanto la fascia ET UX, senza viewport OpenGL.
Palette chiara/scura sintetiche applicate dal test al processo isolato;
non rappresentano un tema FreeCAD installato o una sua certificazione.
Font nativo al 100%, Qt devicePixelRatio 1.0, finestra richiesta 1366×768.

| Densità | Chiaro | Scuro |
| --- | --- | --- |
| Classic Modern | [PNG](classic-light.png) | [PNG](classic-dark.png) |
| Compact Modern | [PNG](compact-light.png) | [PNG](compact-dark.png) |

Le icone e le etichette sono quelle dei comandi nativi FreeCAD, visualizzate
nel contesto dell'host; non sono nuovi asset ET UX redistribuiti come icon set.
Il controllo grafico include testo, separatori e scheda attiva. Gli altri stati,
i font grandi, l'overflow e la navigazione hanno controlli runtime nello smoke.

Rigenerazione nel runtime Linux predisposto:

```sh
ETUX_SCREENSHOT_DIR="$PWD/work/ribbon-captures" bash tools/test_freecad113.sh
```

Lo smoke usa documenti temporanei e ripristina palette/font/densità del test;
le catture sono opzionali. Le quattro tavole in `docs/design/v0.4a/` restano
**concept statici** distinti. Esiti e limiti: [VALIDATION_V04B](../../VALIDATION_V04B.md).
