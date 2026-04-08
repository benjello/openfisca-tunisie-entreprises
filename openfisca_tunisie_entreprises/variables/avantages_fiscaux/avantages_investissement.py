"""Avantages fiscaux à l'investissement — Tunisie.

Les avantages fiscaux accordés aux entreprises tunisiennes se traduisent par des
**déductions de la base imposable** (et non des crédits d'impôt directs, sauf
cas particuliers).

Trois grands régimes sont modélisés ici :

1. Entreprises totalement exportatrices (ETE)
   — Exonération totale d'IS pendant 10 ans, puis taux réduit.
   — Exonération TCL, TFP, FOPROLOS pendant la période d'exonération.
   (Art. 10 CII ; Note commune n° 14/2018)

2. Avantages développement régional (zones prioritaires)
   — Exonération d'IS de 5 à 10 ans selon la zone.
   — Déduction supplémentaire de 25 % à 50 % du CA après la période d'exonération.
   (Art. 23 CII ; Décret n° 99-483 du 1er mars 1999)

3. Déduction pour réinvestissement dans le capital de sociétés résidentes
   — Déduction de 35 % du revenu net réinvesti, dans la limite du bénéfice net.
   — Applicable jusqu'à la fin de la période d'exonération.
   (Art. 7 § III CII ; Art. 11 CIRPPIS ; Note commune n° 1/2017)

Références :
  Code d'Incitations aux Investissements (CII), loi n° 2016-71 du 30 sept. 2016.
  Décret n° 2017-389 du 9 mars 2017 (liste des activités ETE).
  Note commune n° 14/2018 (régimes fiscaux ETE).
  Note commune n° 6/2021 (LF 2021 — modifications du régime IS).
"""

import numpy as np

from openfisca_core.model_api import YEAR, Variable

from openfisca_tunisie_entreprises.entities import Entreprise


# ===========================================================================
# ENTREPRISES TOTALEMENT EXPORTATRICES (ETE)
# ===========================================================================


class annees_dans_regime_ete(Variable):
    value_type = int
    entity = Entreprise
    definition_period = YEAR
    label = "Nombre d'années écoulées depuis l'entrée dans le régime ETE"
    reference = "Art. 10 CII"


class est_regime_ete_actif(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = "L'entreprise est-elle en période d'exonération totale IS (ETE, 10 premières années) ?"
    reference = "Art. 10 CII"

    def formula(entreprise, period):
        ete = entreprise("est_totalement_exportatrice", period)
        annees = entreprise("annees_dans_regime_ete", period)
        return ete & (annees <= 10)


class exoneration_is_ete(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Montant d'IS exonéré au titre du régime ETE (= IS brut pendant les 10 premières années)"
    reference = "Art. 10 CII ; Note commune n° 14/2018"

    def formula(entreprise, period):
        regime_actif = entreprise("est_regime_ete_actif", period)
        is_brut = entreprise("is_brut", period)
        return np.where(regime_actif, is_brut, 0.0)


class taux_is_ete_apres_exoneration(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = "Taux IS applicable aux ETE après la période d'exonération de 10 ans"
    reference = "Art. 10 § 2 CII"

    def formula(entreprise, period):
        ete = entreprise("est_totalement_exportatrice", period)
        annees = entreprise("annees_dans_regime_ete", period)
        taux_normal = entreprise("taux_is_applicable", period)
        # Après 10 ans : IS à taux réduit (15 % / 2 depuis LF 2021, soit 7,5 %)
        # Note : la législation a évolué — on utilise ici le demi-taux
        taux_ete = taux_normal / 2
        return np.where(ete & (annees > 10), taux_ete, taux_normal)


# ===========================================================================
# AVANTAGES ZONES DE DÉVELOPPEMENT RÉGIONAL
# ===========================================================================


class zone_developpement_regional(Variable):
    value_type = int
    entity = Entreprise
    definition_period = YEAR
    label = "Zone de développement régional (0 = hors zone, 1 = premier groupe, 2 = deuxième groupe)"
    reference = "Décret n° 99-483 du 1er mars 1999 ; Décret n° 2017-417"


class duree_exoneration_zone(Variable):
    value_type = int
    entity = Entreprise
    definition_period = YEAR
    label = "Durée d'exonération IS selon la zone de développement régional (années)"
    reference = "Art. 23 CII ; Décret n° 99-483"

    def formula(entreprise, period):
        zone = entreprise("zone_developpement_regional", period)
        # Zone 1 (premier groupe) : 5 ans d'exonération
        # Zone 2 (deuxième groupe) : 10 ans d'exonération
        return np.select(
            [zone == 1, zone == 2],
            [5, 10],
            default=0,
        )


class annees_dans_zone(Variable):
    value_type = int
    entity = Entreprise
    definition_period = YEAR
    label = "Nombre d'années d'activité dans la zone de développement régional"
    reference = "Art. 23 CII"


class est_en_periode_exoneration_zone(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = "L'entreprise est-elle en période d'exonération IS (zone de développement régional) ?"

    def formula(entreprise, period):
        zone = entreprise("zone_developpement_regional", period)
        annees = entreprise("annees_dans_zone", period)
        duree = entreprise("duree_exoneration_zone", period)
        return (zone > 0) & (annees <= duree)


class exoneration_is_zone_developpement(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Montant d'IS exonéré au titre des zones de développement régional"
    reference = "Art. 23 CII"

    def formula(entreprise, period):
        en_exoneration = entreprise("est_en_periode_exoneration_zone", period)
        is_brut = entreprise("is_brut", period)
        return np.where(en_exoneration, is_brut, 0.0)


class taux_deduction_supplementaire_zone(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = "Taux de déduction supplémentaire du CA après la période d'exonération (zone développement)"
    reference = "Art. 23 § 3 CII"

    def formula(entreprise, period):
        zone = entreprise("zone_developpement_regional", period)
        # Après la période d'exonération : déduction de 25 % (zone 1) ou 50 % (zone 2) du bénéfice
        return np.select(
            [zone == 1, zone == 2],
            [0.25, 0.50],
            default=0.0,
        )


class deduction_supplementaire_zone(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Déduction supplémentaire de la base IS après la période d'exonération (zone développement)"
    reference = "Art. 23 § 3 CII"

    def formula(entreprise, period):
        zone = entreprise("zone_developpement_regional", period)
        annees = entreprise("annees_dans_zone", period)
        duree = entreprise("duree_exoneration_zone", period)
        taux = entreprise("taux_deduction_supplementaire_zone", period)
        benefice = entreprise("resultat_fiscal", period)
        apres_exoneration = (zone > 0) & (annees > duree)
        return np.where(apres_exoneration, benefice * taux, 0.0)


# ===========================================================================
# DÉDUCTION POUR RÉINVESTISSEMENT DANS LE CAPITAL (Art. 7 CII / Art. 11 CIRPPIS)
# ===========================================================================


class souscriptions_capital_societes(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Souscriptions au capital de sociétés résidentes (pour déduction Art. 7 CII)"
    reference = "Art. 7 § III CII ; Art. 11 CIRPPIS"


class reinvestissement_dans_fonds_speciaux(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Réinvestissement dans des fonds spéciaux (FCPR, SICAR, etc.)"
    reference = "Art. 7 § IV CII"


class base_reinvestissement_eligible(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Base éligible à la déduction pour réinvestissement (souscriptions + fonds)"

    def formula(entreprise, period):
        capital = entreprise("souscriptions_capital_societes", period)
        fonds = entreprise("reinvestissement_dans_fonds_speciaux", period)
        return capital + fonds


class deduction_reinvestissement_base(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Déduction pour réinvestissement (35 % du bénéfice net réinvesti, plafonnée au bénéfice)"
    reference = "Art. 7 § III CII ; Note commune n° 1/2017"

    def formula(entreprise, period):
        benefice_net = entreprise("resultat_fiscal", period)
        reinvesti = entreprise("base_reinvestissement_eligible", period)
        # La déduction est de 35 % du montant réinvesti, plafonnée au bénéfice net
        deduction = 0.35 * reinvesti
        return np.minimum(deduction, benefice_net)


# ===========================================================================
# SYNTHÈSE — TOTAL DES AVANTAGES FISCAUX IS
# ===========================================================================


class total_exonerations_is(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Total des exonérations IS (ETE + zones développement)"

    def formula(entreprise, period):
        ete = entreprise("exoneration_is_ete", period)
        zones = entreprise("exoneration_is_zone_developpement", period)
        return ete + zones


class is_net_apres_avantages(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "IS net dû après application de tous les avantages fiscaux"
    reference = "Art. 49 CIRPPIS ; Art. 7, 10, 23 CII"

    def formula(entreprise, period):
        is_base = entreprise("is_net_du", period)
        exonerations = entreprise("total_exonerations_is", period)
        degrevement = entreprise("degrevement_reinvestissement", period)
        return np.maximum(is_base - exonerations - degrevement, 0.0)
