"""Produits (revenus) du compte de résultat tunisien.

Structure conforme au Système Comptable des Entreprises (SCE) tunisien
établi par la loi n° 96-112 du 30 décembre 1996 et les normes comptables
tunisiennes (NCT).

Tous les montants sont en dinars tunisiens (DT), hors TVA.
Toutes les variables sont annuelles et portées au niveau de l'Entreprise,
sauf mention contraire.

Comptes concernés (Plan de Comptes Général tunisien) :
  70X : Revenus des ventes de marchandises
  71X : Revenus des ventes de biens (production)
  72X : Revenus des prestations de services
  73X : Variation de stocks de produits finis et en-cours
  74X : Production immobilisée
  75X : Subventions d'exploitation
  76X : Autres produits d'exploitation
  79X : Reprises sur provisions et amortissements
"""

from openfisca_core.model_api import YEAR, Variable

from openfisca_tunisie_entreprises.entities import Entreprise, Etablissement

# ---------------------------------------------------------------------------
# Ventes de marchandises (compte 70)
# ---------------------------------------------------------------------------


class ventes_marchandises_local(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Ventes de marchandises — marché local (HT)"
    reference = "NCT 03 — État de résultat ; comptes 701-702"


class ventes_marchandises_export(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Ventes de marchandises — export (HT)"
    reference = "NCT 03 — État de résultat ; comptes 703-704"


class ventes_marchandises(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Ventes de marchandises — total (HT)"

    def formula(entreprise, period):
        local = entreprise("ventes_marchandises_local", period)
        export = entreprise("ventes_marchandises_export", period)
        return local + export


# ---------------------------------------------------------------------------
# Production vendue — biens (compte 71)
# ---------------------------------------------------------------------------


class production_vendue_biens_local(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Production de biens vendue — marché local (HT)"
    reference = "NCT 03 ; comptes 711-712"


class production_vendue_biens_export(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Production de biens vendue — export (HT)"
    reference = "NCT 03 ; comptes 713-714"


class production_vendue_biens(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Production de biens vendue — total (HT)"

    def formula(entreprise, period):
        local = entreprise("production_vendue_biens_local", period)
        export = entreprise("production_vendue_biens_export", period)
        return local + export


# ---------------------------------------------------------------------------
# Production vendue — services (compte 72)
# ---------------------------------------------------------------------------


class production_vendue_services_local(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Prestations de services — marché local (HT)"
    reference = "NCT 03 ; comptes 721-722"


class production_vendue_services_export(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Prestations de services — export (HT)"
    reference = "NCT 03 ; comptes 723-724"


class production_vendue_services(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Prestations de services — total (HT)"

    def formula(entreprise, period):
        local = entreprise("production_vendue_services_local", period)
        export = entreprise("production_vendue_services_export", period)
        return local + export


# ---------------------------------------------------------------------------
# Chiffre d'affaires (agrégats clés)
# ---------------------------------------------------------------------------


class chiffre_affaires_local(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Chiffre d'affaires local brut (HT) — base TCL et minimum IS"
    reference = "Art. 45 loi 97-11 (TCL) ; Art. 49 ter CIRPPIS (minimum IS)"

    def formula(entreprise, period):
        marchandises = entreprise("ventes_marchandises_local", period)
        biens = entreprise("production_vendue_biens_local", period)
        services = entreprise("production_vendue_services_local", period)
        return marchandises + biens + services


class chiffre_affaires_export(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Chiffre d'affaires à l'export (HT)"

    def formula(entreprise, period):
        marchandises = entreprise("ventes_marchandises_export", period)
        biens = entreprise("production_vendue_biens_export", period)
        services = entreprise("production_vendue_services_export", period)
        return marchandises + biens + services


class chiffre_affaires_brut(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Chiffre d'affaires brut total (local + export, HT)"

    def formula(entreprise, period):
        local = entreprise("chiffre_affaires_local", period)
        export = entreprise("chiffre_affaires_export", period)
        return local + export


# ---------------------------------------------------------------------------
# Chiffre d'affaires local au niveau de l'établissement (base TCL)
# ---------------------------------------------------------------------------


class chiffre_affaires_local_etablissement(Variable):
    value_type = float
    unit = "currency"
    entity = Etablissement
    definition_period = YEAR
    label = "Chiffre d'affaires local de l'établissement (HT) — base de la TCL"
    reference = "Art. 45 loi 97-11 du 3 février 1997 (Code de la fiscalité locale)"


# ---------------------------------------------------------------------------
# Autres produits d'exploitation
# ---------------------------------------------------------------------------


class variation_stocks_produits(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Variation de stocks de produits finis et en-cours (compte 73)"
    reference = "NCT 03"


class production_immobilisee(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Production immobilisée (compte 74)"
    reference = "NCT 03"


class subventions_exploitation(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Subventions d'exploitation reçues (compte 75)"
    reference = "NCT 03"


class autres_produits_exploitation(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Autres produits d'exploitation (compte 76)"
    reference = "NCT 03"


class reprises_provisions_exploitation(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Reprises sur provisions et amortissements d'exploitation (compte 79)"
    reference = "NCT 03"


class revenus_exploitation(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Total des produits d'exploitation (I)"
    reference = "NCT 03 — État de résultat"

    def formula(entreprise, period):
        ca = entreprise("chiffre_affaires_brut", period)
        variation_stocks = entreprise("variation_stocks_produits", period)
        immo = entreprise("production_immobilisee", period)
        subventions = entreprise("subventions_exploitation", period)
        autres = entreprise("autres_produits_exploitation", period)
        reprises = entreprise("reprises_provisions_exploitation", period)
        return ca + variation_stocks + immo + subventions + autres + reprises


# ---------------------------------------------------------------------------
# Produits financiers
# ---------------------------------------------------------------------------


class interets_et_revenus_assimiles(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Intérêts et revenus assimilés (compte 76)"
    reference = "NCT 25"


class gains_de_change(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Gains de change (compte 766)"
    reference = "NCT 15"


class revenus_valeurs_mobilieres(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Revenus de valeurs mobilières et participations (compte 761)"
    reference = "NCT 07"


class autres_produits_financiers(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Autres produits financiers"


class produits_financiers(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Total des produits financiers (III)"

    def formula(entreprise, period):
        interets = entreprise("interets_et_revenus_assimiles", period)
        change = entreprise("gains_de_change", period)
        vm = entreprise("revenus_valeurs_mobilieres", period)
        autres = entreprise("autres_produits_financiers", period)
        return interets + change + vm + autres


# ---------------------------------------------------------------------------
# Produits extraordinaires
# ---------------------------------------------------------------------------


class plus_values_cessions_actifs(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Plus-values sur cessions d'actifs (compte 77)"
    reference = "NCT 05"


class subventions_equilibre(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Subventions d'équilibre et d'investissement (compte 75X)"
    reference = "NCT 12"


class autres_produits_extraordinaires(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Autres produits extraordinaires (compte 77X)"


class reprises_provisions_extraordinaires(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Reprises sur provisions extraordinaires (compte 79X)"


class produits_extraordinaires(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Total des produits extraordinaires (V)"

    def formula(entreprise, period):
        pv = entreprise("plus_values_cessions_actifs", period)
        subv = entreprise("subventions_equilibre", period)
        autres = entreprise("autres_produits_extraordinaires", period)
        reprises = entreprise("reprises_provisions_extraordinaires", period)
        return pv + subv + autres + reprises
