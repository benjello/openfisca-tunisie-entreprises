"""Réintégrations et déductions extracomptables — passage du résultat comptable au résultat fiscal.

Le résultat fiscal est obtenu à partir du résultat comptable (avant IS) en y
ajoutant les **réintégrations** (charges non déductibles fiscalement) et en y
soustrayant les **déductions extracomptables** (produits exonérés ou non imposables).

  Résultat fiscal = Résultat comptable
                   + Réintégrations
                   - Déductions extracomptables
                   - Déficits antérieurs reportables

Références principales :
  Art. 12 à 48  du Code de l'IRPP et de l'IS (charges déductibles)
  Art. 11, 11 bis, 38 à 48 bis du CIRPPIS (déductions)
  Note commune n° 23/2014 (charges non déductibles — amendes et pénalités)
  Note commune n° 7/2020  (déductibilité des dons)
"""

from openfisca_core.model_api import YEAR, Variable

from openfisca_tunisie_entreprises.entities import Entreprise


# ===========================================================================
# RÉINTÉGRATIONS — charges comptabilisées mais non déductibles fiscalement
# ===========================================================================


class reintegration_amendes_penalites(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Réintégration : amendes, pénalités et majorations fiscales et douanières"
    reference = "Art. 14-3° CIRPPIS ; Note commune n° 23/2014"


class reintegration_cadeaux_dons(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Réintégration : cadeaux et dons non déductibles (au-delà des plafonds légaux)"
    reference = "Art. 14-4° CIRPPIS ; Art. 30 CIRPPIS (dons aux œuvres sociales)"


class reintegration_amortissements_excedentaires(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Réintégration : dotations aux amortissements excédentaires (taux > taux fiscaux admis)"
    reference = "Art. 12 CIRPPIS ; Décret n° 2008-492 (taux d'amortissement)"


class reintegration_provisions_non_admises(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Réintégration : provisions non admises fiscalement"
    reference = "Art. 12 CIRPPIS"


class reintegration_interets_excedentaires(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Réintégration : intérêts sur comptes courants associés excédant le taux BCT"
    reference = "Art. 34-IV CIRPPIS"


class reintegration_charges_non_justifiees(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Réintégration : charges sans justificatifs probants ou fictives"
    reference = "Art. 12 CIRPPIS"


class reintegration_charges_paradis_fiscaux(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Réintégration : charges versées à des résidents de paradis fiscaux (non justifiées)"
    reference = "Art. 45 ter CIRPPIS"


class reintegration_quote_part_charges_revenus_exoneres(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Réintégration : quote-part des charges afférentes aux revenus exonérés"
    reference = "Art. 11 CIRPPIS"


class autres_reintegrations(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Autres réintégrations fiscales"


class total_reintegrations(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Total des réintégrations fiscales"

    def formula(entreprise, period):
        amendes = entreprise("reintegration_amendes_penalites", period)
        cadeaux = entreprise("reintegration_cadeaux_dons", period)
        amortissements = entreprise("reintegration_amortissements_excedentaires", period)
        provisions = entreprise("reintegration_provisions_non_admises", period)
        interets = entreprise("reintegration_interets_excedentaires", period)
        injustifiees = entreprise("reintegration_charges_non_justifiees", period)
        paradis = entreprise("reintegration_charges_paradis_fiscaux", period)
        quote_part = entreprise("reintegration_quote_part_charges_revenus_exoneres", period)
        autres = entreprise("autres_reintegrations", period)
        return (
            amendes
            + cadeaux
            + amortissements
            + provisions
            + interets
            + injustifiees
            + paradis
            + quote_part
            + autres
        )


# ===========================================================================
# DÉDUCTIONS EXTRACOMPTABLES — produits non imposables ou bénéfices exonérés
# ===========================================================================


class deduction_dividendes_participation(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Déduction : dividendes et revenus de participations (évitement double imposition)"
    reference = "Art. 38-IV CIRPPIS"


class deduction_revenus_valeurs_mobilieres_rs_liberatoire(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Déduction : revenus de valeurs mobilières soumis à RS libératoire"
    reference = "Art. 38-V CIRPPIS ; Art. 52 bis CIRPPIS"


class deduction_plus_values_reinvesties(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Déduction : plus-values de cession d'actifs réinvesties dans l'entreprise"
    reference = "Art. 11 bis CIRPPIS"


class deduction_benefices_reinvestis(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Déduction : bénéfices réinvestis donnant droit à avantage fiscal (35 % du bénéfice net)"
    reference = "Art. 7 CII ; Art. 11 CIRPPIS ; Note commune n° 1/2017"


class deduction_revenus_export(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Déduction : bénéfices provenant des opérations d'exportation (entreprises partiellement exportatrices)"
    reference = "Art. 11 CIRPPIS ; Art. 10 CII"


class deduction_revenus_zones_developpement(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Déduction : bénéfices exonérés — zones de développement régional"
    reference = "Art. 23 CII ; Décret n° 99-483"


class autres_deductions(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Autres déductions extracomptables"


class total_deductions_extracomptables(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Total des déductions extracomptables"

    def formula(entreprise, period):
        dividendes = entreprise("deduction_dividendes_participation", period)
        rs_lib = entreprise("deduction_revenus_valeurs_mobilieres_rs_liberatoire", period)
        pv = entreprise("deduction_plus_values_reinvesties", period)
        reinvest = entreprise("deduction_benefices_reinvestis", period)
        export = entreprise("deduction_revenus_export", period)
        zones = entreprise("deduction_revenus_zones_developpement", period)
        autres = entreprise("autres_deductions", period)
        return dividendes + rs_lib + pv + reinvest + export + zones + autres


# ===========================================================================
# REPORT DÉFICITAIRE
# ===========================================================================


class deficits_anterieurs_ordinaires_reportes(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Déficits ordinaires des 5 exercices antérieurs imputés sur le résultat fiscal"
    reference = "Art. 48-IX CIRPPIS"


class deficits_anterieurs_amortissements_reportes(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Déficits liés aux amortissements reportés (reportables indéfiniment)"
    reference = "Art. 48-IX CIRPPIS"


class total_deficits_reportes(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Total des déficits antérieurs imputés (ordinaires + amortissements)"

    def formula(entreprise, period):
        ordinaires = entreprise("deficits_anterieurs_ordinaires_reportes", period)
        amortissements = entreprise("deficits_anterieurs_amortissements_reportes", period)
        return ordinaires + amortissements
