   #----------------- marginal gain approach for mix building -----------------------#
import helpers
import itertools
import spray_config


#---------------- cost optimal coverage by stage-----------------------#



def has_activity(row, disease):
    if disease not in row:
        return False

    val = str(row[disease]).strip().lower()
    return spray_config.rating_map.get(val, 0.0) > 0


def cheapest_full_coverage(chem, stage_name):

    weights = spray_config.stage_weights[stage_name]

    # Diseases we must control
    target_diseases = [
        d for d, w in weights.items() if w > 0
    ]

    if not target_diseases:
        return []

    best_cost = float("inf")
    mix = None

    products = list(chem.iterrows())

    # Try combinations of increasing size
    for r in range(1, 4):  # up to 3 products

        for combo in itertools.combinations(products, r):

            rows = [c[1] for c in combo]

            # Check coverage
            covered = set()

            for row in rows:
                for disease in target_diseases:
                    if has_activity(row, disease):
                        covered.add(disease)

            if len(covered) != len(target_diseases):
                continue

            # Compute cost (handles sulfur-sensitive acreage)
            cost = 0
            for row in rows:
                product_name = str(row["Product"]).lower()

                if "sulfur" in product_name:
                    cost += row["Cost/Dose"] * spray_config.NORMAL_ACRES
                else:
                    cost += row["Cost/Dose"] * spray_config.TOTAL_ACRES

            if cost < best_cost:
                best_cost = cost
                mix = rows

        # Stop early if solution found at this size
        if mix is not None:
            break

    return mix, best_cost
