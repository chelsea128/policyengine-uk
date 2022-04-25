from openfisca_core.variables import Variable
from typing import Callable, Type
import h5py
from openfisca_uk.data.datasets.frs.enhanced.stages.imputation.enhanced_frs import (
    EnhancedFRS,
)
from openfisca_uk.repo import REPO
from openfisca_tools.data import Dataset


def baseline_is_nonzero(variable: Type[Variable]) -> Callable:
    """Creates an OpenFisca formula calculating the whether the specified
    variable is non-zero in the baseline.

    Args:
        variable (Type[Variable]): The variable to calculate the change in.

    Returns:
        Callable: The OpenFisca formula.
    """

    def formula(entity, period):
        return entity("baseline_" + variable.__name__, period) > 0

    formula.__doc__ = f"Baseline-requiring formula for {variable.__name__}"
    return formula


def change_over_baseline(variable: Type[Variable]) -> Callable:
    """Creates an OpenFisca formula calculating the change in the
    specified variable over its baseline value.

    Args:
        variable (Type[Variable]): The variable to calculate the change in.

    Returns:
        Callable: The OpenFisca formula.
    """

    def formula(entity, period):
        baseline_value = entity("baseline_" + variable.__name__, period)
        return entity(variable.__name__, period) - baseline_value

    formula.__doc__ = f"Baseline-requiring formula for {variable.__name__}"
    return formula


def generate_baseline_variables(dataset: Dataset, year: int):
    """
    Save baseline values of variables to a H5 dataset.

    Args:
        year (int): The year of the EnhancedFRS to input the results in.
    """

    from openfisca_uk import Microsimulation

    YEARS = list(range(year, 2026))
    baseline = Microsimulation(dataset=dataset, add_baseline_values=False)

    variable_metadata = baseline.simulation.tax_benefit_system.variables

    for variable in variable_metadata:
        if variable[:9] == "baseline_":
            for subyear in YEARS:
                baseline.simulation.set_input(
                    variable,
                    subyear,
                    [True]
                    * len(
                        baseline.calc(
                            variable_metadata[variable].entity.key + "_id"
                        )
                    ),
                )

    # First, find variables which need baseline storage.

    variables = list(
        filter(
            lambda variable: hasattr(variable, "formula")
            and variable.formula.__doc__ is not None
            and "Baseline-requiring formula" in variable.formula.__doc__,
            variable_metadata.values(),
        )
    )
    variables = list(
        map(
            lambda variable: variable_metadata[
                variable.formula.__doc__.split(" for ")[1]
            ],
            variables,
        )
    )
    print(f"Found {len(variables)} variables to store baseline values for:")
    print("\n* " + "\n* ".join([variable.label for variable in variables]))

    existing_dataset = {}
    with dataset.load(year) as data:
        for variable in data.keys():
            existing_dataset[variable] = {}
            for time_period in data[variable].keys():
                existing_dataset[variable][time_period] = data[variable][
                    time_period
                ][...]

        for variable in variables:
            existing_dataset[f"baseline_{variable.name}"] = {}
            for subyear in YEARS:
                existing_dataset[f"baseline_{variable.name}"][
                    subyear
                ] = baseline.calc(variable.name, period=subyear).values

    with h5py.File(dataset.file(year), "w") as f:
        for variable in existing_dataset.keys():
            for time_period in existing_dataset[variable].keys():
                f[f"{variable}/{time_period}"] = existing_dataset[variable][
                    time_period
                ]


if __name__ == "__main__":
    generate_baseline_variables(EnhancedFRS, 2022)
