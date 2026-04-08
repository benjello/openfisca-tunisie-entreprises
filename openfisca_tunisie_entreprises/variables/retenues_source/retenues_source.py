"""Retenues à la source (RS) — Tunisie.

Les retenues à la source sont des prélèvements opérés par le débiteur (l'entreprise
qui verse) sur les sommes payées à des tiers, et reversés à l'État.

Ce module modélise les deux facettes :
  - **Côté débiteur** : RS collectée et reversée au Trésor (obligation légale)
  - **Côté créditeur** : RS subie imputable sur l'IS dû ou restituable

Les RS constituent des acomptes sur l'IS du bénéficiaire, déductibles de son
imposition finale.

Taux en vigueur (Art. 52 CIRPPIS, et lois de finances successives) :

  Honoraires, commissions, courtages (PM résidentes)   :  3 %  (depuis LF 2014)
  Loyers (PM résidentes)                               : 15 %  (depuis LF 2014)
  Loyers (PP)                                          : 15 %
  Dividendes et revenus assimilés                      : 10 %  (depuis LF 2021)
  Intérêts servis aux PP et PM résidentes              : 20 %  (libératoire PP)
  Marchés de l'État et collectivités (PM)              :  3 %
  Revenus des artistes et professions libérales        : 10 % / 15 %

Références :
  Art. 52 à 52 ter du Code de l'IRPP et de l'IS (CIRPPIS).
  Note commune n° 23/2014 (taux RS honoraires et loyers).
  Note commune n° 6/2021 (taux RS dividendes).
  Décret n° 2001-2392 (liste des opérations soumises à RS).
"""

from openfisca_core.model_api import YEAR, Variable

from openfisca_tunisie_entreprises.entities import Entreprise


# ===========================================================================
# CÔTÉ DÉBITEUR — RS collectées par l'entreprise et versées au Trésor
# ===========================================================================


# ---------------------------------------------------------------------------
# Honoraires, commissions, courtages versés à des PM résidentes
# ---------------------------------------------------------------------------


class honoraires_verses_pm(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Honoraires, commissions et courtages versés à des personnes morales résidentes (HT)"
    reference = "Art. 52-I-1° CIRPPIS"


class rs_honoraires_verses(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "RS collectée sur honoraires versés à des PM (3 %)"
    reference = "Art. 52-I-1° CIRPPIS ; Note commune n° 23/2014"

    def formula(entreprise, period, parameters):
        base = entreprise("honoraires_verses_pm", period)
        taux = parameters(period).retenues_source.retenues_honoraires.taux
        return base * taux


# ---------------------------------------------------------------------------
# Loyers versés à des PM résidentes
# ---------------------------------------------------------------------------


class loyers_verses_pm(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Loyers versés à des personnes morales résidentes (HT)"
    reference = "Art. 52-I-3° CIRPPIS"


class rs_loyers_verses_pm(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "RS collectée sur loyers versés à des PM (15 %)"
    reference = "Art. 52-I-3° CIRPPIS ; Note commune n° 23/2014"

    def formula(entreprise, period, parameters):
        base = entreprise("loyers_verses_pm", period)
        taux = parameters(period).retenues_source.retenues_loyers.taux_personnes_morales
        return base * taux


# ---------------------------------------------------------------------------
# Loyers versés à des PP
# ---------------------------------------------------------------------------


class loyers_verses_pp(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Loyers versés à des personnes physiques (HT)"
    reference = "Art. 52-I-3° CIRPPIS"


class rs_loyers_verses_pp(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "RS collectée sur loyers versés à des PP (15 %)"
    reference = "Art. 52-I-3° CIRPPIS"

    def formula(entreprise, period, parameters):
        base = entreprise("loyers_verses_pp", period)
        taux = parameters(period).retenues_source.retenues_loyers.taux_personnes_physiques
        return base * taux


# ---------------------------------------------------------------------------
# Dividendes distribués
# ---------------------------------------------------------------------------


class dividendes_distribues(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Dividendes et revenus assimilés distribués aux actionnaires résidents"
    reference = "Art. 52-I-5° CIRPPIS"


class rs_dividendes(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "RS collectée sur dividendes distribués (10 % depuis LF 2021)"
    reference = "Art. 52-I-5° CIRPPIS ; Note commune n° 6/2021"

    def formula(entreprise, period, parameters):
        base = entreprise("dividendes_distribues", period)
        taux = parameters(period).retenues_source.retenues_dividendes.taux
        return base * taux


# ---------------------------------------------------------------------------
# Marchés de l'État et des collectivités
# ---------------------------------------------------------------------------


class marches_etat_verses(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Paiements effectués sur marchés de l'État, des collectivités et entreprises publiques"
    reference = "Art. 52-I-4° CIRPPIS"


class rs_marches_etat(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "RS collectée sur marchés de l'État (3 %)"
    reference = "Art. 52-I-4° CIRPPIS"

    def formula(entreprise, period, parameters):
        base = entreprise("marches_etat_verses", period)
        taux = parameters(period).retenues_source.retenues_marches.taux
        return base * taux


# ---------------------------------------------------------------------------
# Total RS collectées (côté débiteur)
# ---------------------------------------------------------------------------


class total_rs_collectees(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Total des retenues à la source collectées et à reverser au Trésor"
    reference = "Art. 52 CIRPPIS"

    def formula(entreprise, period):
        hon = entreprise("rs_honoraires_verses", period)
        loyers_pm = entreprise("rs_loyers_verses_pm", period)
        loyers_pp = entreprise("rs_loyers_verses_pp", period)
        div = entreprise("rs_dividendes", period)
        marches = entreprise("rs_marches_etat", period)
        return hon + loyers_pm + loyers_pp + div + marches


# ===========================================================================
# CÔTÉ CRÉDITEUR — RS subies par l'entreprise (imputable sur IS)
# ===========================================================================


class rs_subies_honoraires(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "RS subies sur honoraires perçus (3 %) — acompte IS imputable"
    reference = "Art. 52 bis CIRPPIS"


class rs_subies_loyers(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "RS subies sur loyers perçus (15 %) — acompte IS imputable"
    reference = "Art. 52 bis CIRPPIS"


class rs_subies_marches(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "RS subies sur paiements reçus de l'État (3 %) — acompte IS imputable"
    reference = "Art. 52 bis CIRPPIS"


class total_rs_subies(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Total des RS subies imputable sur IS (côté créditeur)"
    reference = "Art. 52 bis CIRPPIS"

    def formula(entreprise, period):
        hon = entreprise("rs_subies_honoraires", period)
        loyers = entreprise("rs_subies_loyers", period)
        marches = entreprise("rs_subies_marches", period)
        return hon + loyers + marches


# ===========================================================================
# SOLDE IS FINAL (après RS subies et acomptes)
# ===========================================================================


class solde_is_final(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Solde IS final = IS net après avantages − RS subies − acomptes payés"
    reference = "Art. 51 et 52 bis CIRPPIS"

    def formula(entreprise, period):
        is_net = entreprise("is_net_apres_avantages", period)
        rs = entreprise("total_rs_subies", period)
        acomptes = entreprise("acomptes_is_payes", period)
        # Positif = IS à payer ; négatif = crédit restituable
        return is_net - rs - acomptes
