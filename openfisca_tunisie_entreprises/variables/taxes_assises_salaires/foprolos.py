"""Fonds de Promotion des Logements pour les Salariés (FOPROLOS).

Contribution obligatoire des employeurs du secteur privé au financement
de la construction de logements pour leurs salariés.

Mécanisme :
  FOPROLOS = masse salariale brute * 1 %

  — Aucune déduction possible (contrairement à la TFP).
  — Déductible fiscalement comme charge d'exploitation.
  — Applicable à tous les salariés (résidents et non-résidents).

Références :
  Loi n° 77-56 du 3 août 1977 portant création du FOPROLOS.
  Art. 28 CIRPPIS (déductibilité).
  Note commune n° 10/1994.
"""

from openfisca_core.model_api import YEAR, Variable

from openfisca_tunisie_entreprises.entities import Entreprise


class foprolos(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Contribution FOPROLOS = masse salariale brute * 1 %"
    reference = "Loi n° 77-56 du 3 août 1977 ; Art. 28 CIRPPIS"

    def formula(entreprise, period, parameters):
        assiette = entreprise("masse_salariale_brute", period)
        taux = parameters(period).taxes_entreprises.foprolos.taux
        return assiette * taux


class foprolos_comptabilise(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "FOPROLOS comptabilisé en charges fiscales (compte 633)"
    reference = "NCT 03 ; loi n° 77-56"

    def formula(entreprise, period):
        return entreprise("foprolos", period)
