"""Retenues à la source (RS) et avances — Tunisie.

Les retenues à la source sont des prélèvements opérés par le débiteur (l'entreprise
qui verse) sur les sommes payées à des tiers, et reversés à l'État.

Ce module modélise les deux facettes :
  - **Côté débiteur** : RS collectée et reversée au Trésor (obligation légale)
  - **Côté créditeur** : RS subie imputable sur l'IS dû ou restituable

Les RS constituent des acomptes sur l'IS du bénéficiaire, déductibles de son
imposition finale.

Taux en vigueur (Art. 52 CIRPPIS, et lois de finances successives) :

  Honoraires, commissions, courtages (PM résidentes)   :  3 %  (depuis LF 2014)
  Honoraires, commissions, courtages (PP régime réel)  : 10 %  (depuis LF 2021 ; 15 % avant)
  Loyers (PM résidentes)                               : 15 %  (depuis LF 2014)
  Loyers (PP)                                          : 15 %
  Dividendes et revenus assimilés                      : 10 %  (depuis LF 2021)
  Revenus de capitaux mobiliers (intérêts résidents)   : 20 %  (libératoire PP)
  Marchés de l'État et collectivités (PM)              :  3 %
  Avance importation produits de consommation          : 10 %  (Art. 51 ter ; 15 % si non-conforme dès 2024)

Références :
  Art. 51 ter du Code de l'IRPP et de l'IS (avance importation).
  Art. 52 à 52 ter du Code de l'IRPP et de l'IS (CIRPPIS).
  Note commune n° 23/2014 (taux RS honoraires et loyers).
  Note commune n° 6/2021 (taux RS dividendes).
  Art. 14-5 LF 2020-46 (RS honoraires PP réduit à 10 %).
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
# Honoraires, commissions, courtages versés à des PP (régime réel)
# ---------------------------------------------------------------------------


class honoraires_verses_pp(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Honoraires, commissions et courtages versés à des personnes physiques (régime réel, HT)"
    reference = "Art. 52-I-a CIRPPIS ; Art. 14-5 LF 2020-46"


class rs_honoraires_verses_pp(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "RS collectée sur honoraires versés à des PP (15 % avant 2021 ; 10 % dès 2021)"
    reference = "Art. 52-I-a CIRPPIS ; Art. 14-5 LF 2020-46"

    def formula(entreprise, period, parameters):
        base = entreprise("honoraires_verses_pp", period)
        taux = parameters(period).retenues_source.retenues_honoraires.taux_personnes_physiques
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
    label = "RS collectée sur acquisitions ≥ 1 000 DT (1 % pour PM IS taux normal depuis 2021)"
    reference = "Art. 52-I-g CIRPPIS ; Art. 14-6 LF 2020-46 ; Art. 37-8 LF 2024-48"

    def formula(entreprise, period, parameters):
        base = entreprise("marches_etat_verses", period)
        taux = parameters(period).retenues_source.retenues_marches.taux
        return base * taux


# ---------------------------------------------------------------------------
# Revenus de capitaux mobiliers (intérêts) versés à des résidents
# ---------------------------------------------------------------------------


class interets_verses_residents(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Intérêts et revenus de capitaux mobiliers versés à des PP/PM résidentes (hors devises)"
    reference = "Art. 52-I-c CIRPPIS"


class rs_interets_verses(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "RS collectée sur intérêts versés à des résidents (20 % ; libératoire pour PP)"
    reference = "Art. 52-I-c CIRPPIS"

    def formula(entreprise, period, parameters):
        base = entreprise("interets_verses_residents", period)
        taux = parameters(period).retenues_source.retenues_capitaux_mobiliers.taux
        return base * taux


# ---------------------------------------------------------------------------
# Avance à l'importation (Art. 51 ter CIRPPIS)
# ---------------------------------------------------------------------------


class importations_soumises_avance(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Valeur en douane des importations soumises à l'avance (+ droits et taxes exigibles)"
    reference = "Art. 51 ter CIRPPIS ; décret n° 96-500 du 25/03/1996"


class est_conforme_declaration_electronique(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = "L'entreprise respecte ses obligations de déclaration et paiement électroniques"
    reference = "Décret-loi n° 2022-79 (taux majoré à 15 % pour les non-conformes dès 2024)"
    default_value = True


class avance_importation(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Avance IS/IR due à l'importation (10 % ou 15 % si non-conforme dès 2024)"
    reference = "Art. 51 ter CIRPPIS"

    def formula(entreprise, period, parameters):
        base = entreprise("importations_soumises_avance", period)
        conforme = entreprise("est_conforme_declaration_electronique", period)
        params = parameters(period).impot_societes.avance_importation
        taux_conforme = params.taux
        taux_nc = params.taux_non_conforme
        taux = conforme * taux_conforme + (1 - conforme) * taux_nc
        return base * taux


# ---------------------------------------------------------------------------
# Total RS collectées (côté débiteur)
# ---------------------------------------------------------------------------


class total_rs_collectees(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Total des retenues à la source et avances collectées et à reverser au Trésor"
    reference = "Art. 51 ter et 52 CIRPPIS"

    def formula(entreprise, period):
        hon_pm = entreprise("rs_honoraires_verses", period)
        hon_pp = entreprise("rs_honoraires_verses_pp", period)
        loyers_pm = entreprise("rs_loyers_verses_pm", period)
        loyers_pp = entreprise("rs_loyers_verses_pp", period)
        div = entreprise("rs_dividendes", period)
        interets = entreprise("rs_interets_verses", period)
        marches = entreprise("rs_marches_etat", period)
        avance = entreprise("avance_importation", period)
        return hon_pm + hon_pp + loyers_pm + loyers_pp + div + interets + marches + avance


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
    label = "Solde IS final = IS net après avantages - RS subies - acomptes payés"
    reference = "Art. 51 et 52 bis CIRPPIS"

    def formula(entreprise, period):
        is_net = entreprise("is_net_apres_avantages", period)
        rs = entreprise("total_rs_subies", period)
        acomptes = entreprise("acomptes_is_payes", period)
        # Positif = IS à payer ; négatif = crédit restituable
        return is_net - rs - acomptes
