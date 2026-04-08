"""Agrégat des taxes assises sur la masse salariale (TFP + FOPROLOS).

Ces deux taxes sont :
  - calculées sur la masse salariale brute ;
  - déclarées et payées mensuellement (acomptes) ou annuellement ;
  - déductibles de l'IS en tant que charges d'exploitation.

La TFP nette versée à l'ATFP et le FOPROLOS sont totalisés ici pour
alimenter le tableau de bord fiscal de l'entreprise.
"""

from openfisca_core.model_api import YEAR, Variable

from openfisca_tunisie_entreprises.entities import Entreprise


class taxes_assises_salaires(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Total taxes assises sur la masse salariale (TFP nette + FOPROLOS)"

    def formula(entreprise, period):
        tfp = entreprise("tfp_nette", period)
        foprolos = entreprise("foprolos", period)
        return tfp + foprolos


class taux_effectif_taxes_salaires(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = "Taux effectif des taxes sur salaires (taxes / masse salariale brute)"

    def formula(entreprise, period):
        taxes = entreprise("taxes_assises_salaires", period)
        ms = entreprise("masse_salariale_brute", period)
        return taxes / (ms + (ms == 0))
