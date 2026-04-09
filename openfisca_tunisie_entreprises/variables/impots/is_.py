"""Calcul de l'Impôt sur les Sociétés (IS) — Tunisie.

Flux de calcul :

  1. Résultat fiscal = Résultat comptable (avant IS)
                     + Réintégrations
                     - Déductions extracomptables
                     - Déficits antérieurs reportés
                     (planché à 0 : un déficit fiscal n'est pas imposable)

  2. IS brut = Résultat fiscal * taux IS applicable (par catégorie)

  3. TMI (Taux Minimum d'Imposition)
       = CA brut * 0,2 % (depuis LF 2013 — Art. 49 ter CIRPPIS)

  4. IS dû avant dégrèvement = max(IS brut, TMI)
       — TMI non applicable si résultat fiscal ≤ 0
       — TMI non applicable pendant les 5 premières années d'activité
       — TMI non applicable aux entreprises totalement exonérées d'IS

  5. Dégrèvement pour réinvestissement (Art. 7 CII / Art. 11 CIRPPIS)
       = min(IS dû avant dégrèvement, montant du dégrèvement autorisé)

  6. IS net dû = IS dû avant dégrèvement - Dégrèvement

  7. Acomptes provisionnels payés (3 * 30 % de l'IS N-1)

  8. Solde IS à payer (ou crédit) = IS net dû - Acomptes payés

Références :
  Art. 49, 49 ter, 51 du Code de l'IRPP et de l'IS (CIRPPIS)
  Art. 7, 10, 23 du Code d'Incitations aux Investissements (CII)
  Note commune n° 6/2021 (réforme LF 2021 — taux IS)
  Note commune n° 8/2013 (TMI)
"""

import numpy as np
from openfisca_core.model_api import YEAR, Variable

from openfisca_tunisie_entreprises.entities import Entreprise
from openfisca_tunisie_entreprises.variables.caracteristiques_entreprise import CategorieIS

# ===========================================================================
# RÉSULTAT FISCAL
# ===========================================================================


class resultat_fiscal_brut(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Résultat fiscal brut (avant imputation des déficits antérieurs)"
    reference = "Art. 12 à 48 CIRPPIS"

    def formula(entreprise, period):
        resultat_comptable = entreprise("resultat_avant_impot", period)
        reintegrations = entreprise("total_reintegrations", period)
        deductions = entreprise("total_deductions_extracomptables", period)
        return resultat_comptable + reintegrations - deductions


class resultat_fiscal(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Résultat fiscal net (base d'imposition à l'IS)"
    reference = "Art. 49 CIRPPIS"

    def formula(entreprise, period):
        brut = entreprise("resultat_fiscal_brut", period)
        deficits = entreprise("total_deficits_reportes", period)
        # Le résultat fiscal ne peut être négatif (un déficit n'est pas imposé)
        return np.maximum(brut - deficits, 0.0)


class est_en_situation_deficitaire(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = "L'exercice est-il déficitaire sur le plan fiscal ?"

    def formula(entreprise, period):
        brut = entreprise("resultat_fiscal_brut", period)
        deficits = entreprise("total_deficits_reportes", period)
        return (brut - deficits) < 0


# ===========================================================================
# TAUX IS APPLICABLE
# ===========================================================================


class taux_is_applicable(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = "Taux d'IS applicable à l'entreprise (selon catégorie IS)"
    reference = "Art. 49 CIRPPIS ; Note commune n° 6/2021"

    def formula(entreprise, period, parameters):
        categorie = entreprise("categorie_is", period)
        taux = parameters(period).impot_societes.taux

        return np.select(
            [
                categorie == CategorieIS.majore,
                categorie == CategorieIS.normal,
                categorie == CategorieIS.reduit,
                categorie == CategorieIS.intermediaire,
            ],
            [
                taux.taux_majore,
                taux.taux_normal,
                taux.taux_reduit,
                taux.taux_intermediaire,
            ],
            default=taux.taux_normal,
        )


# ===========================================================================
# IS BRUT
# ===========================================================================


class is_brut(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "IS brut = résultat fiscal * taux IS applicable"
    reference = "Art. 49 CIRPPIS"

    def formula(entreprise, period):
        base = entreprise("resultat_fiscal", period)
        taux = entreprise("taux_is_applicable", period)
        return base * taux


# ===========================================================================
# TAUX MINIMUM D'IMPOSITION (TMI)
# ===========================================================================


class annees_activite(Variable):
    value_type = int
    entity = Entreprise
    definition_period = YEAR
    label = "Nombre d'années d'activité de l'entreprise (pour exonération TMI 5 premières années)"
    reference = "Art. 49 ter CIRPPIS"


class est_exonere_is(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = "L'entreprise bénéficie-t-elle d'une exonération totale d'IS ?"
    reference = "Art. 10 CII (entreprises totalement exportatrices) ; Art. 23 CII (zones développement)"


class tmi(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Taux Minimum d'Imposition (TMI) : 0,2 %/500 DT (régime général) ou 0,1 %/300 DT (taux IS 10 %)"
    reference = "Art. 49-II CIRPPIS ; Art. 14-16 LF 2020-46 ; Note commune n° 8/2013"

    def formula(entreprise, period, parameters):
        ca_brut = entreprise("chiffre_affaires_brut", period)
        categorie = entreprise("categorie_is", period)
        p = parameters(period).impot_societes

        est_taux_reduit = categorie == CategorieIS.reduit

        taux_mini = np.where(
            est_taux_reduit,
            p.minimum_impot_taux_reduit,
            p.minimum_impot,
        )
        minimum_absolu = np.where(
            est_taux_reduit,
            p.minimum_impot_absolu_taux_reduit,
            p.minimum_impot_absolu,
        )
        return np.maximum(ca_brut * taux_mini, minimum_absolu)


class tmi_est_applicable(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = "La TMI est-elle applicable ? (non si exonérée, déficitaire, ou < 5 ans d'activité)"
    reference = "Art. 49 ter CIRPPIS"

    def formula(entreprise, period):
        exoneree = entreprise("est_exonere_is", period)
        deficitaire = entreprise("est_en_situation_deficitaire", period)
        anciennete = entreprise("annees_activite", period)
        # TMI applicable uniquement si : non exonérée, non déficitaire, et > 5 ans
        return ~exoneree & ~deficitaire & (anciennete > 5)  # noqa: PLR2004


# ===========================================================================
# IS DÛ AVANT DÉGRÈVEMENT
# ===========================================================================


class is_du_avant_degrevement(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "IS dû avant dégrèvement pour réinvestissement = max(IS brut, TMI)"
    reference = "Art. 49 et 49 ter CIRPPIS"

    def formula(entreprise, period):
        brut = entreprise("is_brut", period)
        tmi_montant = entreprise("tmi", period)
        tmi_applicable = entreprise("tmi_est_applicable", period)
        # Appliquer la TMI uniquement si elle est supérieure à l'IS brut
        return np.where(tmi_applicable, np.maximum(brut, tmi_montant), brut)


# ===========================================================================
# DÉGRÈVEMENT POUR RÉINVESTISSEMENT
# ===========================================================================


class montant_reinvesti_eligible(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Montant effectivement réinvesti et éligible au dégrèvement fiscal"
    reference = "Art. 7 CII ; Art. 11 CIRPPIS"


class degrevement_reinvestissement(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Dégrèvement IS pour réinvestissement (plafonné à 35 % du bénéfice net et à l'IS dû)"
    reference = "Art. 7 CII ; Note commune n° 1/2017"

    def formula(entreprise, period):
        is_avant = entreprise("is_du_avant_degrevement", period)
        resultat = entreprise("resultat_fiscal", period)
        reinvesti = entreprise("montant_reinvesti_eligible", period)
        # Le dégrèvement est égal au montant réinvesti * taux IS,
        # mais plafonné à 35 % du bénéfice net réinvesti et à l'IS dû
        plafond_benefice = 0.35 * resultat
        degrevement_brut = np.minimum(reinvesti, plafond_benefice)
        # Le dégrèvement ne peut pas dépasser l'IS dû
        return np.minimum(degrevement_brut, is_avant)


# ===========================================================================
# IS NET DÛ
# ===========================================================================


class is_net_du(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "IS net dû après dégrèvement pour réinvestissement"
    reference = "Art. 49 CIRPPIS"

    def formula(entreprise, period):
        is_avant = entreprise("is_du_avant_degrevement", period)
        degrevement = entreprise("degrevement_reinvestissement", period)
        return np.maximum(is_avant - degrevement, 0.0)


# ===========================================================================
# ACOMPTES PROVISIONNELS
# ===========================================================================


class is_exercice_precedent(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "IS net dû au titre de l'exercice précédent (N-1) — base de calcul des acomptes"
    reference = "Art. 51 CIRPPIS"


class acomptes_is_payes(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Acomptes IS payés dans l'année (3 * 30 % de l'IS N-1)"
    reference = "Art. 51 CIRPPIS (échéances : 25 juin, 25 sept., 25 déc.)"

    def formula(entreprise, period, parameters):
        is_n1 = entreprise("is_exercice_precedent", period)
        taux_acompte = parameters(period).impot_societes.acomptes_provisionnels.taux_acompte
        # 3 acomptes de 30 % chacun = 90 % de l'IS N-1
        return 3 * taux_acompte * is_n1


class solde_is_a_payer(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Solde IS à payer (ou crédit) à la date du dépôt de la déclaration (25 mars N+1)"
    reference = "Art. 51 CIRPPIS"

    def formula(entreprise, period):
        is_du = entreprise("is_net_du", period)
        acomptes = entreprise("acomptes_is_payes", period)
        # Valeur positive = solde à payer ; valeur négative = crédit d'IS
        return is_du - acomptes
