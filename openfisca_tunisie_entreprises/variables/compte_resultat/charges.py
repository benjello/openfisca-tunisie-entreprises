"""Charges du compte de résultat tunisien.

Structure conforme au Système Comptable des Entreprises (SCE) tunisien
(loi n° 96-112 du 30 décembre 1996 et normes comptables tunisiennes NCT).

Comptes concernés :
  60X : Achats consommés (marchandises, matières, approvisionnements)
  61X : Services extérieurs
  62X : Charges de personnel (salaires)
  63X : Charges sociales et fiscales (CNSS patronal, TFP, FOPROLOS, TCL)
  64X : Dotations aux amortissements
  65X : Dotations aux provisions
  66X : Charges financières
  67X : Autres charges d'exploitation
  68X : Charges extraordinaires
"""

from openfisca_core.model_api import YEAR, Variable

from openfisca_tunisie_entreprises.entities import Entreprise, Etablissement

# ---------------------------------------------------------------------------
# Coût des ventes / achats consommés (comptes 60)
# ---------------------------------------------------------------------------


class achats_marchandises_consommes(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Achats de marchandises consommées (coût d'achat des marchandises vendues)"
    reference = "NCT 03 ; compte 601"


class variation_stocks_marchandises(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Variation de stocks de marchandises (compte 604, signe algébrique)"
    reference = "NCT 03"


class achats_matieres_premieres_consommes(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Achats de matières premières et approvisionnements consommés (compte 602)"
    reference = "NCT 03"


class variation_stocks_matieres(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Variation de stocks de matières premières (compte 605, signe algébrique)"
    reference = "NCT 03"


class cout_des_ventes(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Coût des ventes (achats consommés)"

    def formula(entreprise, period):
        marchandises = entreprise("achats_marchandises_consommes", period)
        var_stock_m = entreprise("variation_stocks_marchandises", period)
        matieres = entreprise("achats_matieres_premieres_consommes", period)
        var_stock_mp = entreprise("variation_stocks_matieres", period)
        return marchandises + var_stock_m + matieres + var_stock_mp


# ---------------------------------------------------------------------------
# Services extérieurs et autres consommations (compte 61)
# ---------------------------------------------------------------------------


class services_exterieurs(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Services extérieurs (loyers, assurances, honoraires, transports, etc.) (compte 61)"
    reference = "NCT 03"


# ---------------------------------------------------------------------------
# Charges de personnel (comptes 62-63) — variables fiscalement importantes
# ---------------------------------------------------------------------------


class salaires_et_appointements(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Salaires et appointements bruts versés aux employés (compte 621)"
    reference = "NCT 03 ; Art. 34 CIRPPIS (déductibilité)"


class avantages_en_nature(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Avantages en nature accordés aux salariés (compte 622)"
    reference = "NCT 03"


class masse_salariale_brute(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Masse salariale brute totale — base TFP et FOPROLOS"
    reference = "Art. 35 loi 88-145 (TFP) ; loi 77-56 (FOPROLOS)"

    def formula(entreprise, period):
        salaires = entreprise("salaires_et_appointements", period)
        avantages = entreprise("avantages_en_nature", period)
        return salaires + avantages


class masse_salariale_brute_etablissement(Variable):
    value_type = float
    unit = "currency"
    entity = Etablissement
    definition_period = YEAR
    label = "Masse salariale brute de l'établissement (pour répartition TFP/FOPROLOS)"
    reference = "Art. 35 loi 88-145 (TFP)"


class cotisations_sociales_patronales(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Cotisations sociales patronales CNSS (compte 631)"
    reference = "Décret n° 2002-2234 du 14 octobre 2002 (taux CNSS)"


# tfp_comptabilisee    → définie dans variables/taxes_assises_salaires/tfp.py
# foprolos_comptabilise → définie dans variables/taxes_assises_salaires/foprolos.py
# tcl_comptabilisee     → définie dans variables/impots/tcl.py


class charges_sociales_et_fiscales(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Charges sociales et fiscales (compte 63) — CNSS patronal, TFP, FOPROLOS, TCL"

    def formula(entreprise, period):
        cnss = entreprise("cotisations_sociales_patronales", period)
        tfp = entreprise("tfp_comptabilisee", period)
        foprolos = entreprise("foprolos_comptabilise", period)
        tcl = entreprise("tcl_comptabilisee", period)
        return cnss + tfp + foprolos + tcl


class charges_personnel(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Total charges de personnel (salaires + charges sociales et fiscales)"

    def formula(entreprise, period):
        salaires = entreprise("masse_salariale_brute", period)
        sociales_fiscales = entreprise("charges_sociales_et_fiscales", period)
        return salaires + sociales_fiscales


# ---------------------------------------------------------------------------
# Dotations aux amortissements (compte 64)
# ---------------------------------------------------------------------------


class dotations_amortissements(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Dotations aux amortissements (compte 64)"
    reference = "NCT 05 — Immobilisations corporelles ; NCT 06 — Immobilisations incorporelles"


# ---------------------------------------------------------------------------
# Dotations aux provisions (compte 65)
# ---------------------------------------------------------------------------


class dotations_provisions_exploitation(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Dotations aux provisions d'exploitation (compte 65)"
    reference = "NCT 03"


# ---------------------------------------------------------------------------
# Autres charges d'exploitation (compte 67)
# ---------------------------------------------------------------------------


class autres_charges_exploitation(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Autres charges d'exploitation (compte 67)"
    reference = "NCT 03"


# ---------------------------------------------------------------------------
# Charges d'exploitation — total
# ---------------------------------------------------------------------------


class charges_exploitation(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Total des charges d'exploitation (II)"
    reference = "NCT 03 — État de résultat"

    def formula(entreprise, period):
        cout_ventes = entreprise("cout_des_ventes", period)
        services = entreprise("services_exterieurs", period)
        personnel = entreprise("charges_personnel", period)
        amortissements = entreprise("dotations_amortissements", period)
        provisions = entreprise("dotations_provisions_exploitation", period)
        autres = entreprise("autres_charges_exploitation", period)
        return cout_ventes + services + personnel + amortissements + provisions + autres


# ---------------------------------------------------------------------------
# Charges financières (compte 66)
# ---------------------------------------------------------------------------


class interets_et_charges_assimiles(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Intérêts et charges assimilées (compte 661)"
    reference = "NCT 25"


class pertes_de_change(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Pertes de change (compte 666)"
    reference = "NCT 15"


class autres_charges_financieres(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Autres charges financières (compte 668)"


class charges_financieres(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Total des charges financières (IV)"

    def formula(entreprise, period):
        interets = entreprise("interets_et_charges_assimiles", period)
        change = entreprise("pertes_de_change", period)
        autres = entreprise("autres_charges_financieres", period)
        return interets + change + autres


# ---------------------------------------------------------------------------
# Charges extraordinaires (compte 68)
# ---------------------------------------------------------------------------


class moins_values_cessions_actifs(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Moins-values sur cessions d'actifs (compte 681)"
    reference = "NCT 05"


class autres_charges_extraordinaires(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Autres charges extraordinaires (compte 688)"


class dotations_provisions_extraordinaires(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Dotations aux provisions extraordinaires (compte 685)"


class charges_extraordinaires(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Total des charges extraordinaires (VI)"

    def formula(entreprise, period):
        mv = entreprise("moins_values_cessions_actifs", period)
        autres = entreprise("autres_charges_extraordinaires", period)
        provisions = entreprise("dotations_provisions_extraordinaires", period)
        return mv + autres + provisions
