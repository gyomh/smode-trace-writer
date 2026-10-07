# Smode Trace Writer

*[English version](README.md)*

> **Expérimental, pas un outil officiel Smode.** Construit par essais et erreurs sur l'API Oil (voir [smode-oil-reference](https://github.com/gyomh/smode-oil-reference)). Testé sur Smode Compose R15.

Un Script réutilisable qui **peint une ligne à partir de la position d'un point mobile** : il lit la position X / Y
d'un ShapeLayer et écrit la valeur Y dans le point de contrôle d'un tracé (`PathShapeGenerator`) à l'index X
correspondant. Il interpole entre l'ancien et le nouvel index pour **ne jamais laisser de trous à haute vitesse**.
Développé pour [smode-oscilloscope](https://github.com/gyomh/smode-oscilloscope).

## Installation

1. Glissez `trace_writer.py` dans votre projet Smode, **Launch Mode = At Every Update** (obligatoire : il lit une
   position en continu).
2. **Test rapide :** laissez `movingShape` et `lineShape` vides et exécutez : une démo complète (point + ligne +
   rampe linéaire en boucle sur X, sinus sur Y) est créée et câblée.
3. **Vos propres formes :** glissez-les dans `movingShape` et `lineShape` **avant le premier lancement** (la démo
   n'est construite que si les deux sont vides). `nPoints` ne sert qu'à la ligne de la démo.

## Licence

MIT — voir [LICENSE](LICENSE).
