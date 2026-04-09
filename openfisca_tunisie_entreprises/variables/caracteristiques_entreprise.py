"""Caractéristiques générales de l'entreprise et de l'établissement.

Ces variables décrivent la nature juridique, le secteur d'activité et les
grandeurs économiques de base nécessaires au calcul de l'IS, de la TCL,
de la TFP et du FOPROLOS.
"""

from openfisca_core.model_api import (
    YEAR,
    Enum,
    Variable,
)

from openfisca_tunisie_entreprises.entities import Entreprise, Etablissement


# ---------------------------------------------------------------------------
# Énumérations
# ---------------------------------------------------------------------------


class FormeJuridique(Enum):
    """Forme juridique de l'entreprise.

    Détermine notamment si la personne est soumise à l'IS ou à l'IR
    en tant que personne physique (entreprise individuelle).
    """

    sa = "Société Anonyme (SA)"
    sarl = "Société à Responsabilité Limitée (SARL)"
    suarl = "Société Unipersonnelle à Responsabilité Limitée (SUARL)"
    snc = "Société en Nom Collectif (SNC)"
    scs = "Société en Commandite Simple (SCS)"
    entreprise_individuelle = "Entreprise individuelle (personne physique)"
    groupement_interet_economique = "Groupement d'intérêt économique (GIE)"
    autre = "Autre forme juridique"


class CategorieIS(Enum):
    """Catégorie déterminant le taux d'IS applicable.

    Quatre catégories depuis la loi de finances 2025 (LF 2024-48 du 09/12/2024) :

    - majore        : 40 % (depuis LF 2025) — banques, établissements financiers
                      (hors établissements de paiement), sociétés d'assurance et de
                      réassurance (y compris mutuelles et takaful).
    - normal        : 20 % (depuis LF 2025, 15 % de LF 2021 à LF 2024) — sociétés
                      résidentes de droit commun.
    - reduit        : 10 % — artisanat, agriculture, pêche, zones de développement
                      régional (après période d'exonération), etc.
    - intermediaire : 35 % (stable) — établissements de paiement, sociétés
                      d'investissement, sociétés de recouvrement de créances,
                      opérateurs de réseaux de télécommunications, grandes surfaces
                      commerciales, concessionnaires automobiles, franchisés d'une
                      marque étrangère.

    Indices entiers (utilisés dans les tests) :
        majore=0  normal=1  reduit=2  intermediaire=3

    Références :
    - Art. 49-I du Code de l'IRPP et de l'IS.
    - Art. 37-1 à 37-3 de la loi de finances n° 2024-48 du 09/12/2024.
    """

    majore = "Taux majoré 40 % (banques, assurances)"
    normal = "Taux normal 20 %"
    reduit = "Taux réduit 10 %"
    intermediaire = "Taux intermédiaire 35 % (télécoms, grandes surfaces, etc.)"


class SecteurActivite(Enum):
    """Grand secteur d'activité économique.

    Utilisé pour déterminer la catégorie IS et le taux de TFP applicable.
    Basé sur la Nomenclature des Activités Tunisiennes (NAT).
    """

    agriculture_peche = "Agriculture et pêche"
    industries_manufacturieres = "Industries manufacturières"
    batiment_travaux_publics = "Bâtiment et travaux publics"
    commerce = "Commerce"
    services = "Services"
    tourisme_hotellerie = "Tourisme et hôtellerie"
    transport = "Transport"
    banque_assurance = "Banque, assurance et services financiers"
    telecom = "Télécommunications"
    immobilier = "Activités immobilières"
    professions_liberales = "Professions libérales et services aux entreprises"
    autre = "Autre secteur"


# ---------------------------------------------------------------------------
# Variables — Entreprise (unité légale)
# ---------------------------------------------------------------------------


class forme_juridique(Variable):
    value_type = Enum
    possible_values = FormeJuridique
    entity = Entreprise
    definition_period = YEAR
    label = "Forme juridique de l'entreprise"
    default_value = FormeJuridique.sarl


class categorie_is(Variable):
    value_type = Enum
    possible_values = CategorieIS
    entity = Entreprise
    definition_period = YEAR
    label = "Catégorie IS (détermine le taux applicable)"
    reference = "Article 49 du Code de l'IRPP et de l'IS"
    default_value = CategorieIS.normal


class secteur_activite(Variable):
    value_type = Enum
    possible_values = SecteurActivite
    entity = Entreprise
    definition_period = YEAR
    label = "Grand secteur d'activité de l'entreprise"
    default_value = SecteurActivite.services


class est_totalement_exportatrice(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = "L'entreprise est-elle totalement exportatrice ?"
    reference = "Art. 10 du Code d'Incitations aux Investissements (CII)"


class est_en_zone_developpement_regional(Variable):
    value_type = bool
    entity = Entreprise
    definition_period = YEAR
    label = "L'entreprise est-elle implantée dans une zone de développement régional ?"
    reference = "Art. 23 du Code d'Incitations aux Investissements (CII)"


# ---------------------------------------------------------------------------
# Variables — Etablissement
# ---------------------------------------------------------------------------


class secteur_activite_etablissement(Variable):
    value_type = Enum
    possible_values = SecteurActivite
    entity = Etablissement
    definition_period = YEAR
    label = "Secteur d'activité de l'établissement"
    default_value = SecteurActivite.services
