#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Générateur expérimental de carrés magiques concentriques d'ordre impair.

Principe :
- on fixe un ordre impair n ;
- le centre vaut (n² + 1) / 2 ;
- on construit le carré de l'intérieur vers l'extérieur ;
- chaque nouvelle couronne utilise les nombres restants les plus petits
  et les plus grands, associés en paires complémentaires ;
- chaque sous-carré central 3x3, 5x5, 7x7, ... reste magique.

Exemples :

python sites/mystimath/scripts/generate_concentric_odd_square.py --order 7 --print

python sites/mystimath/scripts/generate_concentric_odd_square.py --order 9 --seed 42 --out sites/mystimath/src/data/structures/carre-magique-concentrique-ordre-9.json

python sites/mystimath/scripts/generate_concentric_odd_square.py --orders 7 9 11 13 15 --out-dir sites/mystimath/src/data/structures
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from random import Random


def solve_oriented_subset(pairs: list[int], count: int, target: int, center: int):
    """
    Cherche exactement 'count' paires parmi 'pairs'.

    Pour chaque paire basse/haute :
        low + high = 2 * center

    On choisit soit low, soit high, de façon à atteindre 'target'.
    Retourne une liste de tuples :
        [(low, chosen_value), ...]
    """

    states = {(0, 0): []}

    for low in pairs:
        high = 2 * center - low
        new_states = dict(states)

        for (used_count, current_sum), path in list(states.items()):
            if used_count >= count:
                continue

            for chosen_value in (low, high):
                next_sum = current_sum + chosen_value

                if next_sum > target:
                    continue

                key = (used_count + 1, next_sum)

                if key not in new_states:
                    new_states[key] = path + [(low, chosen_value)]

        states = new_states

    return states.get((count, target))


def build_next_border(inner_square: list[list[int]], final_order: int, size: int, rng: Random):
    """
    Ajoute une couronne autour du carré intérieur.

    final_order : ordre final du carré complet.
    size        : ordre de la nouvelle couche construite.
                  Exemple : 3, puis 5, puis 7, etc.
    """

    center = (final_order * final_order + 1) // 2
    inner_size = size - 2

    low_start = center - ((size * size - 1) // 2)
    previous_low = center - ((inner_size * inner_size - 1) // 2)

    lows = list(range(low_start, previous_low))

    expected_pair_count = 2 * size - 2

    if len(lows) != expected_pair_count:
        raise RuntimeError(
            f"Erreur couche {size}x{size} : "
            f"{len(lows)} paires trouvées, {expected_pair_count} attendues."
        )

    corner_pairs = [
        (i, j)
        for i in range(len(lows))
        for j in range(len(lows))
        if i != j
    ]

    rng.shuffle(corner_pairs)

    solution = None

    for index_a, index_b in corner_pairs:
        pair_a = lows[index_a]
        pair_b = lows[index_b]

        orientations_a = [pair_a, 2 * center - pair_a]
        orientations_b = [pair_b, 2 * center - pair_b]

        rng.shuffle(orientations_a)
        rng.shuffle(orientations_b)

        for top_left in orientations_a:
            for top_right in orientations_b:
                remaining_pairs = [
                    value
                    for index, value in enumerate(lows)
                    if index not in (index_a, index_b)
                ]

                rng.shuffle(remaining_pairs)

                # La ligne du haut doit sommer à size * center.
                top_target = size * center - top_left - top_right

                top_solution = solve_oriented_subset(
                    remaining_pairs,
                    size - 2,
                    top_target,
                    center,
                )

                if top_solution is None:
                    continue

                top_lows = {low for low, _ in top_solution}

                left_pairs = [
                    pair
                    for pair in remaining_pairs
                    if pair not in top_lows
                ]

                # La colonne de gauche doit aussi sommer à size * center.
                bottom_left = 2 * center - top_right
                left_target = size * center - top_left - bottom_left

                left_solution = solve_oriented_subset(
                    left_pairs,
                    size - 2,
                    left_target,
                    center,
                )

                if left_solution is None:
                    continue

                solution = {
                    "top_left": top_left,
                    "top_right": top_right,
                    "top_solution": top_solution,
                    "left_solution": left_solution,
                }

                break

            if solution is not None:
                break

        if solution is not None:
            break

    if solution is None:
        raise RuntimeError(f"Aucune bordure valide trouvée pour l'ordre {size}.")

    rng.shuffle(solution["top_solution"])
    rng.shuffle(solution["left_solution"])

    complement = lambda value: 2 * center - value

    square = [[None for _ in range(size)] for _ in range(size)]

    # Placement du carré intérieur.
    for row in range(inner_size):
        for col in range(inner_size):
            square[row + 1][col + 1] = inner_square[row][col]

    # Coins.
    top_left = solution["top_left"]
    top_right = solution["top_right"]

    square[0][0] = top_left
    square[0][size - 1] = top_right
    square[size - 1][0] = complement(top_right)
    square[size - 1][size - 1] = complement(top_left)

    # Ligne du haut et ligne du bas.
    for col, (_, chosen_value) in enumerate(solution["top_solution"], start=1):
        square[0][col] = chosen_value
        square[size - 1][col] = complement(chosen_value)

    # Colonne de gauche et colonne de droite.
    for row, (_, chosen_value) in enumerate(solution["left_solution"], start=1):
        square[row][0] = chosen_value
        square[row][size - 1] = complement(chosen_value)

    if any(any(value is None for value in row) for row in square):
        raise RuntimeError(f"Construction incomplète pour l'ordre {size}.")

    return square


def generate_concentric_square(order: int, seed: int = 42):
    """
    Génère un carré magique concentrique normal d'ordre impair.
    """

    if order < 3:
        raise ValueError("L'ordre doit être supérieur ou égal à 3.")

    if order % 2 == 0:
        raise ValueError("Ce générateur vise les ordres impairs.")

    rng = Random(seed)

    center = (order * order + 1) // 2

    square = [[center]]

    for size in range(3, order + 1, 2):
        square = build_next_border(square, order, size, rng)

    return square


def central_subsquare(square: list[list[int]], size: int):
    """
    Extrait le sous-carré central d'ordre 'size'.
    """

    order = len(square)
    start = (order - size) // 2

    return [
        row[start:start + size]
        for row in square[start:start + size]
    ]


def sums_for(square: list[list[int]]):
    """
    Calcule les sommes des lignes, colonnes et diagonales.
    """

    order = len(square)

    rows = [sum(row) for row in square]

    cols = [
        sum(square[row][col] for row in range(order))
        for col in range(order)
    ]

    diag1 = sum(square[i][i] for i in range(order))
    diag2 = sum(square[i][order - 1 - i] for i in range(order))

    return {
        "rows": rows,
        "cols": cols,
        "diags": [diag1, diag2],
        "all": rows + cols + [diag1, diag2],
    }


def validate_concentric_square(square: list[list[int]]):
    """
    Vérifie :
    - carré normal ;
    - valeurs 1..n² ;
    - aucun doublon ;
    - chaque sous-carré central impair est magique.
    """

    order = len(square)

    report = []
    ok = True

    if order % 2 == 0:
        return False, ["L'ordre est pair. Ce script vise les ordres impairs."]

    if not all(len(row) == order for row in square):
        return False, ["La grille n'est pas carrée."]

    values = [value for row in square for value in row]
    expected_values = set(range(1, order * order + 1))
    actual_values = set(values)

    if len(values) != len(actual_values):
        ok = False
        report.append("Doublons détectés.")

    missing = sorted(expected_values - actual_values)
    extra = sorted(value for value in actual_values if value not in expected_values)

    if missing:
        ok = False
        report.append("Valeurs manquantes : " + ", ".join(map(str, missing)))

    if extra:
        ok = False
        report.append("Valeurs hors plage : " + ", ".join(map(str, extra)))

    if not missing and not extra and len(values) == len(actual_values):
        report.append(f"Valeurs normales validées : 1 à {order * order}.")

    center_index = order // 2
    center = square[center_index][center_index]
    expected_center = (order * order + 1) // 2

    if center != expected_center:
        ok = False
        report.append(f"Centre incorrect : {center}, attendu {expected_center}.")
    else:
        report.append(f"Centre correct : {center}.")

    for size in range(3, order + 1, 2):
        sub = central_subsquare(square, size)
        expected_constant = size * center
        sums = sums_for(sub)

        is_magic = all(value == expected_constant for value in sums["all"])

        interval_half = (size * size - 1) // 2
        interval_start = center - interval_half
        interval_end = center + interval_half

        sub_values = [value for row in sub for value in row]
        expected_interval = set(range(interval_start, interval_end + 1))

        has_expected_interval = set(sub_values) == expected_interval

        if is_magic and has_expected_interval:
            report.append(
                f"Sous-carré {size}x{size} validé, "
                f"constante {expected_constant}, "
                f"valeurs {interval_start}..{interval_end}."
            )
        else:
            ok = False
            report.append(
                f"Sous-carré {size}x{size} invalide. "
                f"Constante attendue {expected_constant}. "
                f"Sommes obtenues : {sums['all']}. "
                f"Intervalle attendu : {interval_start}..{interval_end}."
            )

    return ok, report


def build_layers(square: list[list[int]]):
    """
    Prépare les couches pour le JSON Mystimath.
    """

    order = len(square)
    center = square[order // 2][order // 2]

    layers = []

    for size in range(3, order + 1, 2):
        sub = central_subsquare(square, size)

        layers.append({
            "order": size,
            "constant": size * center,
            "center": center,
            "square": sub,
        })

    return layers


def build_structure_json(square: list[list[int]]):
    """
    Génère une structure JSON compatible avec le dossier src/data/structures.
    """

    order = len(square)
    center = square[order // 2][order // 2]
    constant = order * center

    slug = f"carre-magique-concentrique-ordre-{order}"

    constants = [
        layer["constant"]
        for layer in build_layers(square)
    ]

    return {
        "id": slug,
        "slug": slug,
        "name": f"Carré magique concentrique d’ordre {order}",
        "type": "Carré magique",
        "structureType": "square",
        "dimension": 2,
        "order": order,
        "family": "Carrés magiques classiques",
        "familySlug": "carres-magiques-classiques",
        "subfamily": "Carrés magiques concentriques",
        "difficulty": "intermediaire",
        "difficultySlug": "intermediaire",
        "usage": [
            "visualisation",
            "vérification",
            "exemple concentrique"
        ],
        "usageSlugs": [
            "visualisation",
            "verification",
            "exemple-concentrique"
        ],
        "constructionMethod": "Construction à enceintes",
        "constructionMethodSlug": "construction-a-enceintes",
        "variant": "Concentrique",
        "variantSlug": "concentrique",
        "variantSlugs": [
            "concentrique",
            "a-enceintes",
            "ordre-impair",
            "generation-experimentale"
        ],
        "magicOperations": [
            "addition"
        ],
        "entryConstraints": [
            "entiers consecutifs",
            "entiers distincts"
        ],
        "constant": constant,
        "sumConstant": constant,
        "minEntry": 1,
        "maxEntry": order * order,
        "square": square,
        "concentricLayers": build_layers(square),
        "properties": [
            f"ordre {order}",
            f"somme constante {constant}",
            f"entiers de 1 à {order * order}",
            "entiers distincts",
            "carré magique normal",
            "carré magique concentrique",
            "carré magique à enceintes",
            "sous-carrés centraux impairs magiques",
            "construction par couronnes successives",
            "constantes concentriques : " + ", ".join(map(str, constants))
        ],
        "description": (
            f"Ce carré magique normal d’ordre {order} contient tous les entiers "
            f"de 1 à {order * order}. Chaque ligne, chaque colonne et les deux "
            f"diagonales principales ont pour somme {constant}. Il possède en plus "
            f"une propriété concentrique : chaque sous-carré central impair est "
            f"également magique."
        ),
        "notes": (
            f"Le centre du carré est {center}. Les constantes des sous-carrés "
            f"concentriques sont les multiples impairs de ce centre. "
            f"Cette grille a été générée expérimentalement par un script Mystimath "
            f"de construction par couronnes complémentaires."
        ),
        "status": "generated_verified",
        "origin": "Génération expérimentale Mystimath",
        "period": "Contemporain",
        "attribution": {
            "discoveredBy": "Génération expérimentale Mystimath",
            "usedBy": [
                "Carrés magiques concentriques",
                "Carrés magiques à enceintes",
                "Carrés magiques d’ordre impair",
                "Visualisations Mystimath"
            ],
            "contributedBy": "Mystimath",
            "source": (
                "Construction expérimentale par couronnes complémentaires ; "
                "famille historiquement liée aux carrés magiques à enceintes."
            ),
            "sourceUrl": "",
            "publicationStatus": "draft",
            "license": (
                "Donnée mathématique générée expérimentalement ; "
                "présentation et vérification Mystimath"
            ),
            "notes": (
                "Les carrés magiques à enceintes sont attestés historiquement "
                "dans la tradition arabo-orientale. Cette grille particulière "
                "est produite par un script expérimental et doit être citée "
                "comme génération Mystimath."
            )
        }
    }


def format_square(square: list[list[int]]):
    """
    Affichage lisible en console.
    """

    max_value = max(max(row) for row in square)
    width = len(str(max_value))

    lines = []

    for row in square:
        lines.append(" ".join(str(value).rjust(width) for value in row))

    return "\n".join(lines)


def save_json(square: list[list[int]], path: Path):
    """
    Sauvegarde la structure JSON.
    """

    structure = build_structure_json(square)
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(structure, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Génère des carrés magiques concentriques d'ordre impair."
    )

    parser.add_argument(
        "--order",
        type=int,
        help="Ordre impair à générer, par exemple 7, 9, 11."
    )

    parser.add_argument(
        "--orders",
        type=int,
        nargs="*",
        help="Liste d'ordres impairs à générer, par exemple --orders 7 9 11 13 15."
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Graine aléatoire pour rendre la génération reproductible."
    )

    parser.add_argument(
        "--out",
        type=str,
        help="Chemin de sortie JSON pour un seul ordre."
    )

    parser.add_argument(
        "--out-dir",
        type=str,
        help="Dossier de sortie JSON pour plusieurs ordres."
    )

    parser.add_argument(
        "--print",
        action="store_true",
        help="Affiche la grille dans la console."
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if args.orders:
        orders = args.orders
    elif args.order:
        orders = [args.order]
    else:
        orders = [7]

    if args.out and len(orders) > 1:
        raise ValueError("--out ne peut être utilisé qu'avec un seul ordre.")

    for order in orders:
        print("=" * 72)
        print(f"Génération d'un carré magique concentrique d'ordre {order}")
        print("=" * 72)

        square = generate_concentric_square(
            order=order,
            seed=args.seed + order * 1000,
        )

        is_valid, report = validate_concentric_square(square)

        for line in report:
            print(line)

        if not is_valid:
            print("[ERREUR] La grille générée n'est pas valide.")
            raise SystemExit(1)

        print("[OK] Carré magique concentrique validé.")

        if args.print:
            print()
            print(format_square(square))
            print()

        if args.out:
            output_path = Path(args.out)
            save_json(square, output_path)
            print(f"[OK] JSON sauvegardé : {output_path}")

        if args.out_dir:
            output_dir = Path(args.out_dir)
            output_path = output_dir / f"carre-magique-concentrique-ordre-{order}.json"
            save_json(square, output_path)
            print(f"[OK] JSON sauvegardé : {output_path}")

    print()
    print("[SUCCES] Génération terminée.")


if __name__ == "__main__":
    main()