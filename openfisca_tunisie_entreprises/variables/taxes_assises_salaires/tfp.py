"""Taxe de Formation Professionnelle (TFP).

La TFP est une taxe parafiscale assise sur la masse salariale brute des salariés
résidents. Elle finance la formation professionnelle via l'ATFP (Agence Tunisienne
de la Formation Professionnelle).

Mécanisme :
  TFP brute  = masse salariale brute × taux (1 % industrie / 2 % autres)
  TFP nette  = max(TFP brute − dépenses de formation justifiées, 0)

Les dépenses de formation effectivement engagées et dûment justifiées sont
déductibles de la TFP brute, dans la limite de celle-ci.
La TFP nette est déductible fiscalement (charge d'exploitation).

Références :
  Loi n° 88-145 du 31 décembre 1988 (art. 35-39), intégrée aux art. 31-34 CIRPPIS.
  Décret n° 2002-2234 du 14 octobre 2002.
  Note commune n° 14/2007 (modalités de déduction des dépenses de formation).
"""

import numpy as np

from openfisca_core.model_api import YEAR, Variable

from openfisca_tunisie_entreprises.entities import Entreprise
from openfisca_tunisie_entreprises.variables.caracteristiques_entreprise import SecteurActivite


# ---------------------------------------------------------------------------
# Critère de secteur (détermine le taux applicable)
# ---------------------------------------------------------------------------


class est_secteur_industriel(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = "L'entreprise relève-t-elle du secteur industriel ? (taux TFP 1 % au lieu de 2 %)"
    reference = "Art. 31 CIRPPIS (loi 88-145 du 31/12/1988)"

    def formula(entreprise, period):
        secteur = entreprise("secteur_activite", period)
        return secteur == SecteurActivite.industries_manufacturieres


# ---------------------------------------------------------------------------
# Assiette
# ---------------------------------------------------------------------------


class masse_salariale_residents(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Masse salariale brute des salariés résidents — assiette TFP et FOPROLOS"
    reference = "Art. 31 CIRPPIS"

    def formula(entreprise, period):
        # Par défaut on assimile à la masse salariale brute totale.
        # Si l'entreprise emploie des non-résidents, distinguer ici.
        return entreprise("masse_salariale_brute", period)


# ---------------------------------------------------------------------------
# TFP brute
# ---------------------------------------------------------------------------


class taux_tfp(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = "Taux TFP applicable (1 % industrie / 2 % autres secteurs)"
    reference = "Art. 31 CIRPPIS"

    def formula(entreprise, period, parameters):
        est_industriel = entreprise("est_secteur_industriel", period)
        tfp_params = parameters(period).taxes_entreprises.tfp
        return np.where(
            est_industriel,
            tfp_params.taux_industrie,
            tfp_params.taux_autres_secteurs,
        )


class tfp_brute(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "TFP brute = masse salariale résidents × taux TFP"
    reference = "Art. 31 CIRPPIS"

    def formula(entreprise, period):
        assiette = entreprise("masse_salariale_residents", period)
        taux = entreprise("taux_tfp", period)
        return assiette * taux


# ---------------------------------------------------------------------------
# Dépenses de formation déductibles
# ---------------------------------------------------------------------------


class depenses_formation_engagees(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Dépenses de formation professionnelle effectivement engagées et justifiées"
    reference = "Art. 32 CIRPPIS ; Note commune n° 14/2007"


class depenses_formation_deductibles(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Dépenses de formation imputables sur la TFP (plafonnées à la TFP brute)"
    reference = "Art. 32 CIRPPIS"

    def formula(entreprise, period):
        depenses = entreprise("depenses_formation_engagees", period)
        plafond = entreprise("tfp_brute", period)
        return np.minimum(depenses, plafond)


# ---------------------------------------------------------------------------
# TFP nette due
# ---------------------------------------------------------------------------


class tfp_nette(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "TFP nette due = max(TFP brute − dépenses de formation déductibles, 0)"
    reference = "Art. 32-33 CIRPPIS"

    def formula(entreprise, period):
        brute = entreprise("tfp_brute", period)
        deduction_formation = entreprise("depenses_formation_deductibles", period)
        return np.maximum(brute - deduction_formation, 0.0)


# ---------------------------------------------------------------------------
# Lien avec le compte de résultat
# Le module charges.py contient tfp_comptabilisee (stub).
# On crée une formule ici pour la calculer automatiquement.
# ---------------------------------------------------------------------------


class tfp_comptabilisee(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "TFP comptabilisée en charges (= TFP brute ; la déduction formation réduit le versement, pas la charge)"
    reference = "NCT 03 ; Art. 31 CIRPPIS"

    def formula(entreprise, period):
        # La charge comptabilisée est la TFP brute.
        # La déduction des dépenses de formation réduit le versement en numéraire
        # à l'ATFP, mais la charge totale (formation + TFP nette) reste la même.
        return entreprise("tfp_brute", period)
