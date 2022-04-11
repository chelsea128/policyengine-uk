from .in_total import (
    HouseholdsInTotal,
)
from .by_region_by_council_tax_band import (
    HouseholdsByRegionByCouncilTaxBand,
)
from .by_region_by_tenure_type import (
    HouseholdsByRegionByTenureType,
)
from openfisca_uk.data.datasets.frs.enhanced.stages.calibration.losses.loss_category import combine_loss_categories


Households = combine_loss_categories(
    HouseholdsInTotal,
    HouseholdsByRegionByCouncilTaxBand,
    HouseholdsByRegionByTenureType,
    label="Households",
)
