   #----------------- marginal gain approach for mix building -----------------------#
import helpers
import itertools
import spray_config


#---------------- cost optimal coverage by stage-----------------------#



def has_activity(row, disease):
    if disease not in row:
        return False

    val = str(row[disease]).strip().lower()
    return spray_config.rating_map.get(val, 0.0) > spray_config.MINIMUM_SPRAY_EFFECTIVENESS


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


#  Builds a cost-optimal mix that covers all diseases for the stage, respecting rotation and critical period rules
def build_cost_optimal_mix(
    materials,
    stage,
    stage_weights,
    frac_history,
    sulfur_sensitive=False,
    max_products=3,
):

    target_diseases = [d for d, w in stage_weights.items() if w > 0]
    if not target_diseases:
        return []

    need_active = stage in spray_config.CRITICAL_STAGES

    best_mix = None
    best_cost = float("inf")

    candidates = materials.copy()

    if sulfur_sensitive and "SulfurSensitive" in candidates.columns:
        candidates = candidates[candidates["SulfurSensitive"] != "Yes"]

    # Pre-filter useful products
    candidates = candidates[
        candidates.apply(lambda r: helpers.covers_diseases(r, target_diseases), axis=1)
    ]

    for r in range(1, max_products + 1):
        for combo in itertools.combinations(candidates.index, r):

            mix = candidates.loc[list(combo)]

            # --- Must contain multisite backbone ---
            if not any(helpers.is_multisite(row) for _, row in mix.iterrows()):
                continue

            # --- Active required during critical periods ---
            if need_active:
                if all(helpers.is_multisite(row) for _, row in mix.iterrows()):
                    continue

            # --- FRAC rotation ---
            all_fracs = []
            for _, row in mix.iterrows():
                all_fracs += helpers.normalize_frac(row["FRAC"])

            if helpers.violates_rotation(all_fracs, frac_history):
                continue

            # --- Disease coverage ---
            covered = set()
            for _, row in mix.iterrows():
                for d in target_diseases:
                    if helpers.effectiveness(row, d) > 0:
                        covered.add(d)

            if covered != set(target_diseases):
                continue

            cost = mix["Cost/Dose"].sum()

            if cost < best_cost:
                best_cost = cost
                best_mix = mix

    return best_mix


# Builds the seasonal plan by applying the cost-optimal mix builder to each spray date, while tracking FRAC usage and respecting rotation rules and critical period requirements
def optimize_season(schedule, materials, sulfur_acres=1, total_acres=4):

    frac_history = {}
    season_plan = []

    for spray in schedule:

        stage = spray["stage"]
        weights = spray["stage_weights"]

        mix = build_cost_optimal_mix(
            materials,
            stage,
            weights,
            frac_history,
            sulfur_sensitive=(sulfur_acres > 0),
        )

        if mix is None:
            season_plan.append({"date": spray["date"], "mix": "NO VALID MIX"})
            continue

        # Update FRAC history
        all_fracs = []
        for _, row in mix.iterrows():
            all_fracs += helpers.normalize_frac(row["FRAC"])

        helpers.update_frac_history(all_fracs, frac_history)

        season_plan.append(
            {
                "date": spray["date"],
                "stage": stage,
                "products": list(mix["Product"]),
                "Cost/Dose": mix["Cost/Dose"].sum(),
            }
        )

    return season_plan