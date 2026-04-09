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

import numpy as np

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


class reintegration_charges_vehicules_tourisme(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Réintégration : charges non déductibles sur véhicules de tourisme > 9 CV (amortissement, carburant, entretien excédentaires)"
    reference = "Art. 14-5° CIRPPIS"


class reintegration_jetons_presence(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Réintégration : jetons de présence excédant le plafond déductible (1 % masse salariale)"
    reference = "Art. 12 CIRPPIS"


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
        vehicules = entreprise("reintegration_charges_vehicules_tourisme", period)
        jetons = entreprise("reintegration_jetons_presence", period)
        autres = entreprise("autres_reintegrations", period)
        return (
            amendes + cadeaux + amortissements + provisions + interets
            + injustifiees + paradis + quote_part + vehicules + jetons + autres
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
    label = "Déduction : bénéfices d'exportation (⅔ jusqu'en 2020 ; supprimée dès 2021 — Art. 11 bis § V CIRPPIS)"
    reference = "Art. 11 bis § V CIRPPIS ; Art. 41 LF 2019-78 ; Loi n° 2017-8 du 14/02/2017"

    def formula(entreprise, period, parameters):
        # Utiliser le résultat comptable (avant ajustements fiscaux) pour éviter la circularité :
        # resultat_fiscal_brut dépend lui-même de cette déduction.
        resultat_comptable = entreprise("resultat_avant_impot", period)
        taux_export = entreprise("taux_exportation", period)
        taux_deduction = parameters(period).impot_societes.deduction_export.taux
        # Quote-part du résultat comptable attribuable à l'export, déductible au taux applicable
        # (⅔ jusqu'en 2020 ; 0 dès 2021 — le paramètre gère la transition automatiquement)
        benefice_export = np.maximum(resultat_comptable * taux_export, 0.0)
        return benefice_export * taux_deduction


class deduction_revenus_zones_developpement(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Déduction : bénéfices exonérés — zones de développement régional"
    reference = "Art. 23 CII ; Décret n° 99-483"


# ---------------------------------------------------------------------------
# Amortissements supplémentaires (30 %) — Art. 12 bis VIII et IX CIRPPIS
# ---------------------------------------------------------------------------


class est_secteur_eligible_amortissement_supplementaire(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = "Le secteur est-il éligible à l'amortissement supplémentaire sur équipements industriels ?"
    reference = "Art. 12 bis VIII CIRPPIS — exclusions : financier, énergie hors ENR, mines, immobilier, restauration, commerce, télécom"
    default_value = True


class valeur_equipements_industriels_acquis(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Valeur d'acquisition des équipements industriels éligibles (extension/renouvellement, 1re année)"
    reference = "Art. 12 bis VIII CIRPPIS"


class valeur_equipements_enr_acquis(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Valeur d'acquisition des équipements ENR éligibles (1re année ; attestation ministère énergie requise)"
    reference = "Art. 12 bis IX CIRPPIS"


class deduction_amortissement_supplementaire(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Déduction supplémentaire amortissements 30 % (équipements industriels + ENR)"
    reference = "Art. 12 bis VIII et IX CIRPPIS (Loi n° 2017-8 du 14/02/2017)"

    def formula(entreprise, period, parameters):
        p = parameters(period).impot_societes.amortissement_supplementaire
        eligible = entreprise("est_secteur_eligible_amortissement_supplementaire", period)

        # Équipements industriels — conditionnés à l'éligibilité sectorielle
        base_industrie = entreprise("valeur_equipements_industriels_acquis", period)
        ded_industrie = np.where(eligible, base_industrie * p.taux_equipements_industriels, 0.0)

        # ENR — tous secteurs (pas de condition sectorielle)
        base_enr = entreprise("valeur_equipements_enr_acquis", period)
        ded_enr = base_enr * p.taux_equipements_enr

        return ded_industrie + ded_enr


# ---------------------------------------------------------------------------
# Dons et mécénats déductibles — Art. 12-5° et 5 bis CIRPPIS
# ---------------------------------------------------------------------------


class dons_oeuvres_sociales(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Dons aux œuvres sociales des entreprises (déductibles dans la limite des plafonds légaux)"
    reference = "Art. 12-5° CIRPPIS"


class mecenat_culturel(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Mécénats culturels avec approbation ministère de la culture (déductibles)"
    reference = "Art. 12-5 bis CIRPPIS (Ajouté Art. 49-1 LFC 2014-54 du 19/08/2014)"


class deduction_dons_mecenat(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Total déduction dons et mécénats (dons sociaux + mécénat culturel)"
    reference = "Art. 12-5° et 5 bis CIRPPIS ; Note commune n° 7/2020"

    def formula(entreprise, period):
        dons = entreprise("dons_oeuvres_sociales", period)
        mecenat = entreprise("mecenat_culturel", period)
        return dons + mecenat


# ---------------------------------------------------------------------------
# Intérêts emprunts obligataires verts / sociaux — Art. 11 bis II bis CIRPPIS
# ---------------------------------------------------------------------------


class interets_emprunts_verts(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Intérêts d'emprunts obligataires verts, sociaux ou durables perçus (avant plafonnement)"
    reference = "Art. 11 bis II bis CIRPPIS (Ajouté Art. 29 LF 2022 décret-loi n° 2021-21)"


class deduction_interets_emprunts_verts(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Déduction intérêts emprunts obligataires verts/sociaux/durables (plafond 10 000 DT/an)"
    reference = "Art. 11 bis II bis CIRPPIS (LF 2022)"

    def formula(entreprise, period, parameters):
        interets = entreprise("interets_emprunts_verts", period)
        plafond = parameters(period).impot_societes.deduction_interets_verts.plafond
        return np.minimum(interets, plafond)


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
        nouvelles = entreprise("deduction_benefices_nouvelles_entreprises", period)
        amort_supp = entreprise("deduction_amortissement_supplementaire", period)
        dons = entreprise("deduction_dons_mecenat", period)
        interets_verts = entreprise("deduction_interets_emprunts_verts", period)
        autres = entreprise("autres_deductions", period)
        return (
            dividendes + rs_lib + pv + reinvest + export + zones
            + nouvelles + amort_supp + dons + interets_verts + autres
        )


# ===========================================================================
# REPORT DÉFICITAIRE (Art. 48-IX CIRPPIS)
#
# Règle légale :
#   - Déficits ordinaires : reportables sur les 5 exercices suivants uniquement.
#   - Déficits liés aux amortissements : reportables indéfiniment.
#
# Modélisation : un input par exercice déficitaire (N-1 à N-5) pour les
# déficits ordinaires. La limite de 5 ans est ainsi structurellement garantie
# (il n'existe pas de variable pour N-6 ou au-delà).
# ===========================================================================


class deficit_ordinaire_annee_n1(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Déficit ordinaire de l'exercice N-1 reportable (plafonné au déficit déclaré)"
    reference = "Art. 48-IX CIRPPIS"


class deficit_ordinaire_annee_n2(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Déficit ordinaire de l'exercice N-2 reportable"
    reference = "Art. 48-IX CIRPPIS"


class deficit_ordinaire_annee_n3(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Déficit ordinaire de l'exercice N-3 reportable"
    reference = "Art. 48-IX CIRPPIS"


class deficit_ordinaire_annee_n4(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Déficit ordinaire de l'exercice N-4 reportable"
    reference = "Art. 48-IX CIRPPIS"


class deficit_ordinaire_annee_n5(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Déficit ordinaire de l'exercice N-5 reportable (dernière année dans la limite légale)"
    reference = "Art. 48-IX CIRPPIS"


class deficits_anterieurs_ordinaires_reportes(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Total des déficits ordinaires des 5 exercices antérieurs imputables sur le résultat fiscal"
    reference = "Art. 48-IX CIRPPIS"

    def formula(entreprise, period):
        n1 = entreprise("deficit_ordinaire_annee_n1", period)
        n2 = entreprise("deficit_ordinaire_annee_n2", period)
        n3 = entreprise("deficit_ordinaire_annee_n3", period)
        n4 = entreprise("deficit_ordinaire_annee_n4", period)
        n5 = entreprise("deficit_ordinaire_annee_n5", period)
        return n1 + n2 + n3 + n4 + n5


class deficits_anterieurs_amortissements_reportes(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Déficits liés aux amortissements des exercices antérieurs (reportables indéfiniment)"
    reference = "Art. 48-IX CIRPPIS"


class total_deficits_reportes(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Total des déficits antérieurs imputés (ordinaires ≤ 5 ans + amortissements illimités)"
    reference = "Art. 48-IX CIRPPIS"

    def formula(entreprise, period):
        ordinaires = entreprise("deficits_anterieurs_ordinaires_reportes", period)
        amortissements = entreprise("deficits_anterieurs_amortissements_reportes", period)
        return ordinaires + amortissements
