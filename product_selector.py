   #----------------- marginal gain approach for mix building -----------------------#
from logging import critical

import helpers
import itertools
import spray_config
import critcal_period 



#  Builds a cost-optimal mix that covers all diseases for the stage, respecting rotation and critical period rules
def build_cost_optimal_mix(
    materials,
    stage,
    stage_weights,
    frac_history,
    spray_date,
    product_usage
):
    
    # Filter out diseases that have no weight for the current stage, as they are not relevant for this spray.
    target_diseases = helpers.get_target_diseases(stage, stage_weights)

    # Get high  priority diseases for the current stage, based on the stage weights and the HIGH_PRIORITY_THRESHOLD defined in spray_config.py
    high_priority = {
        d for d in target_diseases
        if stage_weights[d] >= spray_config.HIGH_PRIORITY_THRESHOLD
    }

    # Determine if current stage is a critical period  
    is_stage_critical = stage in spray_config.CRITICAL_STAGES

    # Filter candidates that have any activity against target diseases and are allowed by PHI based on if its a crtical period or not. During critical periods, we will be more strict about PHI and prioritize products that are allowed by PHI for the spray date.
    candidates = critcal_period.get_candidates(is_stage_critical, materials, target_diseases, spray_date)



    # -------------------------------------------------------
    # Try increasingly relaxed constraints
    # -------------------------------------------------------

    # Iterate through allowed number of products in the mix, starting from 1 up to MAX_PRODUCTS_PER_SPRAY
    for product_number in range(1, spray_config.MAX_PRODUCTS_PER_SPRAY):

        # Generate all combinations of candidates with the current allowed number of products sorted by
        # least expensive (Cost/Dose) first. This ensures that we are always considering the cheapest options first.
        for product_id in itertools.combinations(candidates.sort_values("Cost/Dose").index, product_number):

            # Get a list of products in the current combination
            mix = candidates.loc[list(product_id)]

            multisite_flags = [helpers.is_multisite(r) for _, r in mix.iterrows()]
            has_multisite = any(multisite_flags)
            has_active = any(not m for m in multisite_flags)

            # # Multisite required always
            if not has_multisite:
                continue

            
            # Critical → prefer active
            # make sure mix has an active ingredient before movin on to the next spray date.
            if critical and not has_active:
                continue

            # ------------------------------------------------
            # Disease coverage
            # ------------------------------------------------

            covered, active_covered = helpers.get_covered_diseases(mix, target_diseases)
            if covered != set(target_diseases):
                continue

            # ------------------------------------------------
            # Prefer actives for high-priority diseases
            # (but don't require all)
            # ------------------------------------------------

            # if critical and high_priority:
            #     coverage_ratio = (
            #         len(high_priority & active_covered) /
            #         len(high_priority)
            #     )

            #     if coverage_ratio <= 0.5:
            #         continue

            # ------------------------------------------------
            # FRAC rotation (soft constraint)
            # ------------------------------------------------

            # all_fracs = []
            # for _, row in mix.iterrows():
            #     all_fracs += helpers.normalize_frac(row["FRAC"])

            # if helpers.violates_rotation(all_fracs, frac_history):
            #     # Skip only if we still have room to search
            #     if product_number <= spray_config.MAX_PRODUCTS_PER_SPRAY:
            #         continue


            # if helpers.violates_max_applications(mix, product_usage):
            #     continue

            return mix

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