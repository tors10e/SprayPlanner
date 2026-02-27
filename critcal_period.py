import helpers
import spray_config

# Fu
def get_candidates(critical, materials, target_diseases, spray_date):
    if critical:
        candidates = materials[
            materials.apply(
                lambda r: (
                    any(helpers.effectiveness(r, d) > spray_config.MINIMUM_SPRAY_EFFECTIVENESS for d in target_diseases)
                    and helpers.allowed_by_phi(r, spray_date)
                ),
                axis=1
            )
        ]
    else:
        candidates = materials[
            materials.apply(
                lambda r: (
                    any(helpers.effectiveness(r, d) > spray_config.MINIMUM_SPRAY_EFFECTIVENESS for d in target_diseases)
                    and helpers.allowed_by_phi(r, spray_date)
                    and helpers.is_multisite(r)
                ),
                axis=1
            )
        ]
    return candidates
