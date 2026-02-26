   #----------------- marginal gain approach for mix building -----------------------#
import helpers
import itertools
import spray_config
import critcal_period 

#---------------- cost optimal coverage by stage-----------------------#



def has_activity(row, disease):
    if disease not in row:
        return False

    val = str(row[disease]).strip().lower()
    return spray_config.rating_map.get(val, 0.0) > spray_config.MINIMUM_SPRAY_EFFECTIVENESS



#  Builds a cost-optimal mix that covers all diseases for the stage, respecting rotation and critical period rules
def build_cost_optimal_mix(
    materials,
    stage,
    stage_weights,
    frac_history,
    spray_date,
    product_usage
):

    target_diseases = [d for d, w in stage_weights.items() if w > 0]
    if not target_diseases:
        return None

    # Determin if current stage is a critical period  
    critical = stage in spray_config.CRITICAL_STAGES

    # Filter candidates that have any activity against target diseases and are allowed by PHI based on if its a crtical period or not. During critical periods, we will be more strict about PHI and prioritize products that are allowed by PHI for the spray date.
    candidates = critcal_period.get_candidates(critical, materials, target_diseases, spray_date)

    high_priority = {
        d for d in target_diseases
        if stage_weights[d] >= spray_config.HIGH_PRIORITY_THRESHOLD
    }

    # -------------------------------------------------------
    # Try increasingly relaxed constraints
    # -------------------------------------------------------

    for allowed_products in range(1, spray_config.MAX_PRODUCTS_PER_SPRAY + 3):

        for combo in itertools.combinations(candidates.index, allowed_products):

            mix = candidates.loc[list(combo)]

            multisite_flags = [helpers.is_multisite(r) for _, r in mix.iterrows()]
            has_multisite = any(multisite_flags)
            has_active = any(not m for m in multisite_flags)

            # Multisite required always
            if not has_multisite:
                continue

            
            # Critical → prefer active
            # make sure mix has an active ingredient before movin on to the next spray date.
            if critical and not has_active:
                continue

            # ------------------------------------------------
            # Disease coverage
            # ------------------------------------------------

            covered = set()
            active_covered = set()

            for _, row in mix.iterrows():
                for d in target_diseases:
                    if helpers.effectiveness(row, d) > 0:
                        covered.add(d)
                        if not helpers.is_multisite(row):
                            active_covered.add(d)

            if covered != set(target_diseases):
                continue

            # ------------------------------------------------
            # Prefer actives for high-priority diseases
            # (but don't require all)
            # ------------------------------------------------

            if critical and high_priority:
                coverage_ratio = (
                    len(high_priority & active_covered) /
                    len(high_priority)
                )

                if coverage_ratio <= 0.5:
                    continue

            # ------------------------------------------------
            # FRAC rotation (soft constraint)
            # ------------------------------------------------

            all_fracs = []
            for _, row in mix.iterrows():
                all_fracs += helpers.normalize_frac(row["FRAC"])

            if helpers.violates_rotation(all_fracs, frac_history):
                # Skip only if we still have room to search
                if allowed_products <= spray_config.MAX_PRODUCTS_PER_SPRAY:
                    continue


            if helpers.violates_max_applications(mix, product_usage):
                continue
            # ------------------------------------------------
            # Choose lowest cost
            # ------------------------------------------------

            return mix.sort_values("Cost/Dose")

    return None


# Builds the seasonal plan by applying the cost-optimal mix builder to each spray date, while tracking FRAC usage and respecting rotation rules and critical period requirements
def optimize_season(schedule, materials, total_acres=4):

    frac_history = {}
    season_plan = []
    product_usage = {}

    for spray in schedule:

        stage = spray["stage"]
        weights = spray["stage_weights"]

        mix = build_cost_optimal_mix(
            materials,
            stage,
            weights,
            frac_history,
            spray["date"],
            product_usage
        )

        if mix is None:
            season_plan.append({"date": spray["date"], "mix": "NO VALID MIX"})
            continue

        for _, row in mix.iterrows():
            product = row["Product"]
            product_usage[product] = product_usage.get(product, 0) + 1

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
                "FRACs": list(mix["FRAC"]),
                "Cost/Dose": mix["Cost/Dose"].sum(),
                "Total Cost": mix["Cost/Dose"].sum() * total_acres,
            }
        )

    return season_plan