"""Agrégats de résultats du compte de résultat tunisien.

Structure de l'état de résultat (SCE — NCT 03) :

  Revenus d'exploitation (I)
- Charges d'exploitation (II)
= Résultat d'exploitation (I - II)
+ Résultat financier (III - IV) = Produits financiers - Charges financières
= Résultat ordinaire avant impôt
+ Résultat extraordinaire (V - VI) = Produits extraordinaires - Charges extraordinaires
= Résultat avant impôt (résultat comptable)
- IS / IR (calculé dans variables/impots/)
= Résultat net de l'exercice

Le résultat comptable est le point de départ du passage au résultat fiscal
(réintégrations et déductions extracomptables, calculées en Phase 3).
"""

from openfisca_core.model_api import YEAR, Variable

from openfisca_tunisie_entreprises.entities import Entreprise


class marge_brute(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Marge brute (chiffre d'affaires - coût des ventes)"

    def formula(entreprise, period):
        ca = entreprise("chiffre_affaires_brut", period)
        cout = entreprise("cout_des_ventes", period)
        return ca - cout


class resultat_exploitation(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Résultat d'exploitation (I - II)"
    reference = "NCT 03 — État de résultat"

    def formula(entreprise, period):
        produits = entreprise("revenus_exploitation", period)
        charges = entreprise("charges_exploitation", period)
        return produits - charges


class resultat_financier(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Résultat financier (III - IV)"
    reference = "NCT 03 ; NCT 25"

    def formula(entreprise, period):
        produits = entreprise("produits_financiers", period)
        charges = entreprise("charges_financieres", period)
        return produits - charges


class resultat_ordinaire_avant_impot(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Résultat ordinaire avant impôt (exploitation + financier)"
    reference = "NCT 03 — État de résultat"

    def formula(entreprise, period):
        exploitation = entreprise("resultat_exploitation", period)
        financier = entreprise("resultat_financier", period)
        return exploitation + financier


class resultat_extraordinaire(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Résultat extraordinaire (V - VI)"
    reference = "NCT 03"

    def formula(entreprise, period):
        produits = entreprise("produits_extraordinaires", period)
        charges = entreprise("charges_extraordinaires", period)
        return produits - charges


class resultat_avant_impot(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Résultat avant impôt (résultat comptable de l'exercice)"
    reference = "NCT 03 — État de résultat"

    def formula(entreprise, period):
        ordinaire = entreprise("resultat_ordinaire_avant_impot", period)
        extraordinaire = entreprise("resultat_extraordinaire", period)
        return ordinaire + extraordinaire


class impot_exercice(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "IS / IR imputé au titre de l'exercice (calculé dans variables/impots/)"
    reference = "Art. 49 CIRPPIS"


class resultat_net(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Résultat net de l'exercice (après IS/IR)"
    reference = "NCT 03 — État de résultat"

    def formula(entreprise, period):
        avant_impot = entreprise("resultat_avant_impot", period)
        impot = entreprise("impot_exercice", period)
        return avant_impot - impot


# ---------------------------------------------------------------------------
# Ratios utiles pour les contrôles fiscaux
# ---------------------------------------------------------------------------


class taux_marge_brute(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = "Taux de marge brute (marge brute / CA brut)"

    def formula(entreprise, period):
        marge = entreprise("marge_brute", period)
        ca = entreprise("chiffre_affaires_brut", period)
        # Éviter la division par zéro
        return marge / (ca + (ca == 0))


class taux_exportation(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = "Part des recettes à l'export dans le CA total"
    reference = "Utilisé pour les avantages entreprises exportatrices (Art. 10 CII)"

    def formula(entreprise, period):
        export = entreprise("chiffre_affaires_export", period)
        total = entreprise("chiffre_affaires_brut", period)
        return export / (total + (total == 0))
