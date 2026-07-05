# Définition de la famille concentrique utilisée par Mystimath

Ce document précise la définition utilisée dans les scripts expérimentaux du dossier `concentric-magic-squares`.

## 1. Carré magique normal

Un carré magique normal d’ordre `n` est une grille `n×n` contenant exactement les entiers de `1` à `n²`, chacun utilisé une seule fois.

La constante magique du carré complet est :

```text
M_n = n × (n² + 1) / 2
````

## 2. Cas impair

Dans cette expérimentation, on s’intéresse aux ordres impairs :

```text
n = 3, 5, 7, 9, 11, ...
```

Le centre du carré vaut :

```text
C = (n² + 1) / 2
```

## 3. Carré magique concentrique

Un carré magique normal impair est dit concentrique, dans le cadre de cette expérimentation, si chaque sous-carré central impair est lui aussi magique.

Exemple pour `n = 7` :

```text
7×7 magique
5×5 central magique
3×3 central magique
```

## 4. Intervalles centrés

La définition utilisée ici impose également que chaque sous-carré central d’ordre `k` utilise l’intervalle centré attendu autour du pivot `C`.

Pour un sous-carré d’ordre `k`, les valeurs attendues sont :

```text
C - (k² - 1) / 2   jusqu’à   C + (k² - 1) / 2
```

Exemple pour un carré global d’ordre `7` :

```text
C = 25

3×3 : 21..29
5×5 : 13..37
7×7 : 1..49
```

Exemple pour un carré global d’ordre `9` :

```text
C = 41

3×3 : 37..45
5×5 : 29..53
7×7 : 17..65
9×9 : 1..81
```

## 5. Constantes concentriques

Si un sous-carré central d’ordre `k` est magique et centré sur `C`, sa constante est :

```text
M_k = k × C
```

Exemple pour `n = 9` :

```text
C = 41

3×3 : 123
5×5 : 205
7×7 : 287
9×9 : 369
```

## 6. Construction par couronnes

Les scripts construisent les carrés de l’intérieur vers l’extérieur.

Chaque nouvelle étape ajoute une couronne autour du carré déjà construit :

```text
1×1 → 3×3 → 5×5 → 7×7 → ...
```

Chaque couronne est formée avec des paires complémentaires autour du centre.

Pour un ordre global `n`, les paires complémentaires ont pour somme :

```text
n² + 1
```

Exemple pour `n = 7` :

```text
1 + 49 = 50
2 + 48 = 50
...
24 + 26 = 50
```

## 7. Portée de cette définition

Cette définition est volontairement stricte.

Elle ne prétend pas couvrir toutes les variantes historiques possibles des carrés magiques à enceintes.

Elle sert à :

* générer des exemples vérifiables ;
* produire des résultats reproductibles ;
* distinguer clairement les carrés générés des carrés choisis éditorialement ;
* documenter une famille mathématique précise dans Mystimath.

