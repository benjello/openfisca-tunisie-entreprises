"""Avantages fiscaux à l'investissement — Tunisie.

Les avantages fiscaux accordés aux entreprises tunisiennes se traduisent par des
**déductions de la base imposable** (et non des crédits d'impôt directs, sauf
cas particuliers).

Quatre grands régimes sont modélisés ici :

1. Entreprises totalement exportatrices (ETE)
   — Exonération totale d'IS pendant 10 ans, puis taux réduit.
   (Art. 10 CII ; Note commune n° 14/2018)

2. Avantages développement régional (zones prioritaires)
   — Exonération d'IS de 5 à 10 ans selon la zone.
   — Déduction supplémentaire de 25 % à 50 % du bénéfice après la période.
   (Art. 23 CII ; Décret n° 99-483 du 1er mars 1999)

3. Déduction pour réinvestissement (physique et financier)
   — Physique : profits réinvestis en biens d'équipement nécessaires à l'exploitation.
   — Financier : souscriptions au capital de sociétés résidentes / fonds spéciaux.
   — Déduction de 35 % du bénéfice net réinvesti, plafonnée au bénéfice.
   (Art. 7 § I et § III CII ; Art. 11 CIRPPIS ; Note commune n° 1/2017)

4. Déduction pour nouvelles entreprises (régime dégressive 4 ans)
   — 100 % / 75 % / 50 % / 25 % selon l'année d'activité (secteurs éligibles).
   — Exonération totale 4 ans pour entreprises créées en 2018-2019 ou 2024-2025.
   — Secteurs exclus : financier, énergie (sauf ENR), mines, promotion immobilière,
     restauration/hébergement, commerce, opérateurs télécom.
   (Art. 11 CIRPPIS version loi n° 2017-8 ; Art. 13 LF 2018 ; Art. 33 LF 2024)

Références :
  Code d'Incitations aux Investissements (CII), loi n° 2016-71 du 30 sept. 2016.
  Loi n° 2017-8 du 14 février 2017 portant refonte du dispositif des avantages fiscaux.
  Note commune n° 14/2018 (régimes fiscaux ETE).
  Note commune n° 6/2021 (LF 2021 — modifications du régime IS).
"""

import numpy as np
from openfisca_core.model_api import YEAR, Variable

from openfisca_tunisie_entreprises.entities import Entreprise

# Constantes métier
DUREE_EXONERATION_ETE = 10  # Art. 10 CII : 10 années d'exonération totale IS
ZONE_PREMIER_GROUPE = 1  # Premier groupe de zones de développement régional
ZONE_DEUXIEME_GROUPE = 2  # Deuxième groupe de zones de développement régional

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
        return ete & (annees <= DUREE_EXONERATION_ETE)


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
        return np.where(ete & (annees > DUREE_EXONERATION_ETE), taux_ete, taux_normal)


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
            [zone == ZONE_PREMIER_GROUPE, zone == ZONE_DEUXIEME_GROUPE],
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
            [zone == ZONE_PREMIER_GROUPE, zone == ZONE_DEUXIEME_GROUPE],
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
# DÉDUCTION POUR RÉINVESTISSEMENT — physique et financier (Art. 7 CII / Art. 11 CIRPPIS)
# ===========================================================================


class investissement_biens_equipement(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Profits réinvestis en biens d'équipement nécessaires à l'exploitation (hors voitures tourisme > 9 CV)"
    reference = "Art. 7 § I CII ; Note commune n° 1/2017"


class souscriptions_capital_societes(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Souscriptions au capital de sociétés résidentes (pour déduction Art. 7 § III CII)"
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
    label = "Base éligible à la déduction pour réinvestissement (équipements + souscriptions + fonds)"
    reference = "Art. 7 § I, § III et § IV CII"

    def formula(entreprise, period):
        equipements = entreprise("investissement_biens_equipement", period)
        capital = entreprise("souscriptions_capital_societes", period)
        fonds = entreprise("reinvestissement_dans_fonds_speciaux", period)
        return equipements + capital + fonds


class deduction_reinvestissement_base(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Déduction pour réinvestissement (35 % du montant réinvesti, plafonnée au bénéfice net)"
    reference = "Art. 7 § I et § III CII ; Note commune n° 1/2017"

    def formula(entreprise, period):
        benefice_net = entreprise("resultat_fiscal", period)
        reinvesti = entreprise("base_reinvestissement_eligible", period)
        deduction = 0.35 * reinvesti
        return np.minimum(deduction, benefice_net)


# ===========================================================================
# DÉDUCTION POUR NOUVELLES ENTREPRISES — régime dégressive 4 ans (Art. 11 CII / Loi 2017-8)
#
# Secteurs éligibles : tout sauf financier, énergie (sauf ENR), mines,
# promotion immobilière, restauration/hébergement, commerce, télécom.
#
# Déduction dégressive (droit commun) :
#   Année 1 : 100 % du bénéfice d'exploitation
#   Année 2 :  75 %
#   Année 3 :  50 %
#   Année 4 :  25 %
#   Année 5+:   0 %
#
# Exonération totale 4 ans (régime spécial LF 2018 / LF 2024) :
#   100 % pendant les 4 premières années pour entreprises créées en 2018-2019
#   ou en 2024-2025.
# ===========================================================================


class annees_depuis_creation(Variable):
    value_type = int
    entity = Entreprise
    definition_period = YEAR
    label = "Nombre d'années d'activité effective depuis la création de l'entreprise"
    reference = "Art. 11 CIRPPIS ; Loi n° 2017-8 du 14/02/2017"


class est_secteur_eligible_exoneration_creation(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = "Le secteur est-il éligible à la déduction pour nouvelles entreprises ?"
    reference = (
        "Art. 11 CIRPPIS (Loi n° 2017-8) — exclusions : financier, énergie hors ENR, "
        "mines, immobilier, restauration, commerce, télécom"
    )
    default_value = True


class beneficie_exoneration_totale_creation(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = "L'entreprise bénéficie-t-elle de l'exonération totale 4 ans (créée en 2018-2019 ou 2024-2025) ?"
    reference = "Art. 13 LF 2018-56 ; Art. 33 LF 2024-48"
    default_value = False


class quotite_deduction_creation(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = "Quote-part du bénéfice déductible au titre du régime nouvelles entreprises (0 à 1)"
    reference = "Art. 11 CIRPPIS (Loi n° 2017-8) ; Art. 13 LF 2018 ; Art. 33 LF 2024"

    def formula(entreprise, period, parameters):
        annees = entreprise("annees_depuis_creation", period)
        eligible = entreprise("est_secteur_eligible_exoneration_creation", period)
        exoneration_totale = entreprise("beneficie_exoneration_totale_creation", period)
        p = parameters(period).impot_societes.nouvelles_entreprises

        # Régime spécial : exonération totale (durée et taux issus des paramètres)
        duree_totale = p.duree_exoneration_totale
        quotite_speciale = np.where(annees <= duree_totale, p.deduction_exoneration_totale, 0.0)

        # Régime droit commun : déduction dégressive (durée et taux issus des paramètres)
        duree_degressif = p.duree_regime_degressif
        quotite_degressive = np.select(
            [annees == 1, annees == 2, annees == 3, annees == duree_degressif],  # noqa: PLR2004
            [p.deduction_annee_1, p.deduction_annee_2, p.deduction_annee_3, p.deduction_annee_4],
            default=0.0,
        )

        quotite = np.where(exoneration_totale, quotite_speciale, quotite_degressive)
        return np.where(eligible, quotite, 0.0)


class deduction_benefices_nouvelles_entreprises(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Déduction IS pour nouvelles entreprises (régime dégressive ou exonération totale 4 ans)"
    reference = "Art. 11 CIRPPIS (Loi n° 2017-8) ; Art. 13 LF 2018 ; Art. 33 LF 2024"

    def formula(entreprise, period):
        # Utiliser le résultat comptable pour éviter la circularité avec resultat_fiscal_brut
        # qui dépend lui-même de total_deductions_extracomptables (dont cette déduction fait partie)
        resultat = entreprise("resultat_avant_impot", period)
        quotite = entreprise("quotite_deduction_creation", period)
        return np.maximum(resultat * quotite, 0.0)


# ===========================================================================
# EXONÉRATION AGRICULTURE ET PÊCHE (Art. 65 CII ; Art. 11 bis V CIRPPIS)
#
# Investissements directs dans l'agriculture et la pêche :
#   - Exonération totale IS pendant 10 ans (Art. 65 CII)
#   - Après 10 ans : déduction des ⅔ du bénéfice (Art. 11 bis V CIRPPIS)
#     La déduction ⅔ post-exonération est gérée via deduction_revenus_zones_developpement
#     si applicable, ou peut rester en stub via autres_deductions.
# ===========================================================================


class est_investissement_agriculture_peche(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = "L'entreprise réalise-t-elle des investissements directs dans l'agriculture ou la pêche (CII) ?"
    reference = "Art. 65 CII (loi n° 2016-71 du 30/09/2016)"
    default_value = False


class annees_dans_regime_agriculture_peche(Variable):
    value_type = int
    entity = Entreprise
    definition_period = YEAR
    label = "Nombre d'années depuis l'entrée dans le régime agriculture/pêche (pour suivi des 10 ans)"
    reference = "Art. 65 CII"


class exoneration_is_agriculture_peche(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Montant d'IS exonéré au titre du régime agriculture/pêche (10 premières années)"
    reference = "Art. 65 CII"

    def formula(entreprise, period, parameters):
        eligible = entreprise("est_investissement_agriculture_peche", period)
        annees = entreprise("annees_dans_regime_agriculture_peche", period)
        is_brut = entreprise("is_brut", period)
        duree = parameters(period).impot_societes.agriculture_peche.duree_exoneration
        return np.where(eligible & (annees <= duree), is_brut, 0.0)


# ===========================================================================
# RÉGIME OFFSHORE — banques et établissements financiers (lois 85-108 / 85-109)
#
# LIMITES DE CETTE IMPLÉMENTATION :
#   Les lois n° 85-108 et n° 85-109 du 06/12/1985 ne sont pas disponibles dans
#   les sources markdown utilisées. Les dispositions codées ci-dessous reflètent
#   les principes généraux connus ; elles doivent être vérifiées et complétées
#   à partir du texte législatif original et de ses modifications successives.
#
# Ce qui est codé :
#   - Indicateur d'appartenance au régime offshore (banque ou étab. financier)
#   - Option entre forfait annuel (stub — montant non vérifiable) et IS de droit commun
#   - Exonération IS lorsque le forfait est choisi (l'IS du droit commun ne s'applique pas)
#
# Ce qui N'est PAS codé (données manquantes) :
#   - Montant exact du forfait annuel en devises (historiquement ~25 000 USD ; a évolué)
#   - Conditions précises d'éligibilité et de sortie du régime
#   - Traitement des opérations mixtes (résidents / non-résidents)
#   - Régime des sociétés commerciales offshore → absorbé dans ETE depuis CII 2016 (déjà codé)
#
# Références :
#   Loi n° 85-108 du 06/12/1985 portant encouragement d'organismes financiers et bancaires
#     travaillant essentiellement avec les non-résidents (banques offshore).
#   Loi n° 85-109 du 06/12/1985 relative aux établissements financiers offshore.
#   CII 2016 — loi n° 2016-71 du 30/09/2016 (absorption des sociétés offshore dans l'ETE).
# ===========================================================================


class est_banque_offshore(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = "L'entreprise est-elle une banque ou un établissement financier offshore (lois 85-108/85-109) ?"
    reference = "Loi n° 85-108 du 06/12/1985 ; Loi n° 85-109 du 06/12/1985"
    default_value = False


class opte_pour_forfait_offshore(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = "L'établissement offshore opte-t-il pour le forfait annuel en devises (au lieu de l'IS) ?"
    reference = "Loi n° 85-108 du 06/12/1985 — Art. non identifié (texte non disponible)"
    default_value = True


class contribution_forfaitaire_offshore(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = (
        "Contribution forfaitaire annuelle offshore en DT (stub — montant en devises "
        "à convertir ; historiquement ~25 000 USD, évolutions non vérifiées)"
    )
    reference = "Loi n° 85-108 du 06/12/1985 (montant exact non disponible)"


class exoneration_is_offshore(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "Montant d'IS exonéré pour les établissements offshore ayant opté pour le forfait"
    reference = "Loi n° 85-108 du 06/12/1985 ; Loi n° 85-109 du 06/12/1985"

    def formula(entreprise, period):
        offshore = entreprise("est_banque_offshore", period)
        forfait = entreprise("opte_pour_forfait_offshore", period)
        is_brut = entreprise("is_brut", period)
        # Lorsque l'option forfait est retenue, l'IS de droit commun ne s'applique pas
        return np.where(offshore & forfait, is_brut, 0.0)


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
        agriculture = entreprise("exoneration_is_agriculture_peche", period)
        offshore = entreprise("exoneration_is_offshore", period)
        return ete + zones + agriculture + offshore


class is_net_apres_avantages(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "IS net dû après application de tous les avantages fiscaux"
    reference = "Art. 49 CIRPPIS ; Art. 7, 10, 23 CII"

    def formula(entreprise, period):
        # is_net_du contient déjà la soustraction du dégrèvement réinvestissement
        # (dans is_.py) — ne pas le soustraire une seconde fois ici.
        is_base = entreprise("is_net_du", period)
        exonerations = entreprise("total_exonerations_is", period)
        return np.maximum(is_base - exonerations, 0.0)
