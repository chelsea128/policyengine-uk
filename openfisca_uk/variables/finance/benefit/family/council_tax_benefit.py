from openfisca_uk.model_api import *


class council_tax_benefit_reported(Variable):
    value_type = float
    entity = Person
    label = u"Council Tax Benefit (reported)"
    documentation = "Reported amount of Council Tax Benefit"
    definition_period = YEAR


class council_tax_benefit(Variable):
    value_type = float
    entity = BenUnit
    label = u"Council Tax Benefit"
    definition_period = YEAR

    def formula(benunit, period, parameters):
        return aggr(benunit, period, ["council_tax_benefit_reported"])
