#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comptage exact des carrés magiques concentriques impairs
dans la famille stricte à couronnes complémentaires.

Définition comptée ici :
- ordre impair n ;
- valeurs normales 1..n² ;
- centre = (n² + 1) / 2 ;
- chaque sous-carré central impair k×k utilise l'intervalle centré attendu ;
- chaque couronne est construite avec des paires complémentaires ;
- les carrés sont d'abord comptés bruts, puis réduits par rotations/réflexions.

Exemples :
python concentric-magic-squares/count_concentric_odd_squares.py --orders 5 7
python concentric-magic-squares/count_concentric_odd_squares.py --order 7
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from functools import reduce
from math import factorial
from operator import mul


def product(values):
    return reduce(mul, values, 1)


def layer_low_values(layer_size: int, center: int) -> list[int]:
    """
    Renvoie les valeurs basses des paires complémentaires utilisées
    par la nouvelle couronne.

    Pour une couche k×k :
    - le sous-carré k×k utilise l'intervalle centré autour du centre ;
    - le sous-carré précédent (k-2)×(k-2) utilisait un intervalle plus petit ;
    - la couronne utilise les valeurs entre ces deux intervalles.
    """

    inner_size = layer_size - 2

    low_start = center - ((layer_size * layer_size - 1) // 2)
    previous_low = center - ((inner_size * inner_size - 1) // 2)

    return list(range(low_start, previous_low))


def build_orientation_sum_maps(lows: list[int], center: int):
    """
    Pour chaque sous-ensemble de paires complémentaires, calcule :
    somme possible -> nombre d'orientations.

    Exemple :
    paire basse 3, centre 25 => paire (3, 47)
    On peut choisir 3 ou 47.

    Les positions ne sont pas encore comptées ici, seulement les orientations.
    """

    pair_count = len(lows)
    total_masks = 1 << pair_count

    maps = [defaultdict(int) for _ in range(total_masks)]
    maps[0][0] = 1

    for index, low in enumerate(lows):
        high = 2 * center - low
        bit = 1 << index

        for mask in range(bit):
            for current_sum, count in maps[mask].items():
                maps[mask | bit][current_sum + low] += count
                maps[mask | bit][current_sum + high] += count

    return maps


def popcount(value: int) -> int:
    return value.bit_count()


def iter_submasks_with_size(mask: int, wanted_size: int):
    """
    Itère sur les sous-masques de taille donnée.
    """

    sub = mask

    while sub:
        if popcount(sub) == wanted_size:
            yield sub

        sub = (sub - 1) & mask

    if wanted_size == 0:
        yield 0


def count_layer_borders(layer_size: int, center: int) -> int:
    """
    Compte le nombre de bordures possibles pour agrandir un carré
    concentrique de taille (k-2)×(k-2) vers k×k.

    La bordure est décrite par :
    - une ligne du haut ;
    - une colonne gauche interne ;
    - les autres côtés sont déterminés par complémentarité.
    """

    if layer_size < 3 or layer_size % 2 == 0:
        raise ValueError("La couche doit être impaire et >= 3.")

    lows = layer_low_values(layer_size, center)
    pair_count = len(lows)

    expected_pair_count = 2 * layer_size - 2

    if pair_count != expected_pair_count:
        raise RuntimeError(
            f"Couche {layer_size}x{layer_size} : "
            f"{pair_count} paires trouvées, {expected_pair_count} attendues."
        )

    complement = lambda value: 2 * center - value

    maps = build_orientation_sum_maps(lows, center)

    internal_count = layer_size - 2
    internal_factor = factorial(internal_count) ** 2

    full_mask = (1 << pair_count) - 1

    total = 0

    for top_left_pair_index, top_left_low in enumerate(lows):
        top_left_bit = 1 << top_left_pair_index

        for top_left in (top_left_low, complement(top_left_low)):
            for top_right_pair_index, top_right_low in enumerate(lows):
                if top_right_pair_index == top_left_pair_index:
                    continue

                top_right_bit = 1 << top_right_pair_index

                for top_right in (top_right_low, complement(top_right_low)):
                    used_corners_mask = top_left_bit | top_right_bit
                    remaining_mask = full_mask ^ used_corners_mask

                    top_target = layer_size * center - top_left - top_right

                    bottom_left = complement(top_right)
                    left_target = layer_size * center - top_left - bottom_left

                    for top_internal_mask in iter_submasks_with_size(
                        remaining_mask,
                        internal_count,
                    ):
                        left_internal_mask = remaining_mask ^ top_internal_mask

                        top_orientations = maps[top_internal_mask].get(top_target, 0)

                        if top_orientations == 0:
                            continue

                        left_orientations = maps[left_internal_mask].get(left_target, 0)

                        if left_orientations == 0:
                            continue

                        total += (
                            top_orientations
                            * left_orientations
                            * internal_factor
                        )

    return total


def count_concentric_order(order: int):
    """
    Compte les carrés concentriques de l'ordre demandé.

    Retourne :
    - les comptes par couche ;
    - le total brut ;
    - le total modulo rotations/réflexions.
    """

    if order < 3 or order % 2 == 0:
        raise ValueError("L'ordre doit être impair et >= 3.")

    center = (order * order + 1) // 2

    layer_counts = []

    for layer_size in range(3, order + 1, 2):
        count = count_layer_borders(layer_size, center)

        layer_counts.append({
            "layer": layer_size,
            "count": count,
        })

    raw_total = product(item["count"] for item in layer_counts)

    # Avec des entrées toutes distinctes, aucun carré normal non trivial
    # ne peut être invariant par une rotation ou une réflexion non triviale.
    reduced_total = raw_total // 8

    return {
        "order": order,
        "center": center,
        "layer_counts": layer_counts,
        "raw_total": raw_total,
        "reduced_total": reduced_total,
    }


def format_int(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compte les carrés magiques concentriques impairs."
    )

    parser.add_argument(
        "--order",
        type=int,
        help="Ordre impair à compter, par exemple 5 ou 7.",
    )

    parser.add_argument(
        "--orders",
        type=int,
        nargs="*",
        help="Liste d'ordres impairs à compter, par exemple --orders 5 7.",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if args.orders:
        orders = args.orders
    elif args.order:
        orders = [args.order]
    else:
        orders = [5, 7]

    for order in orders:
        print("=" * 72)
        print(f"Comptage des carrés magiques concentriques d'ordre {order}")
        print("=" * 72)

        result = count_concentric_order(order)

        print(f"Centre : {result['center']}")
        print()

        print("Comptes par couche :")

        for item in result["layer_counts"]:
            print(
                f"  couche {item['layer']}x{item['layer']} : "
                f"{format_int(item['count'])}"
            )

        print()
        print(f"Total brut : {format_int(result['raw_total'])}")
        print(
            "Total hors rotations/réflexions : "
            f"{format_int(result['reduced_total'])}"
        )
        print()

        if order >= 7:
            print(
                "Note : le total brut est trop grand pour une génération "
                "matérielle complète fichier par fichier."
            )
            print()


if __name__ == "__main__":
    main()