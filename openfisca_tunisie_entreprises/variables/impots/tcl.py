"""Taxe sur les établissements à caractère industriel, commercial ou professionnel (TCL).

La TCL est une taxe locale annuelle due par chaque établissement exerçant une
activité industrielle, commerciale ou professionnelle.

Elle est perçue au profit des collectivités locales (communes, gouvernorats).

Mécanisme (par établissement) :
  TCL brute  = CA brut local de l'établissement × 0,2 %
  TCL due    = max(TCL brute, minimum légal)
               sauf si l'établissement est exonéré

Agrégation entreprise :
  TCL totale = Σ TCL due des établissements rattachés

La TCL est déductible fiscalement en tant que charge d'exploitation (compte 638).

Références :
  Loi n° 97-11 du 3 février 1997 (art. 45 et suivants).
  Code de la fiscalité locale (CFL).
  Note commune n° 2/1998 (modalités d'application de la TCL).
"""

import numpy as np

from openfisca_core.model_api import YEAR, Variable

from openfisca_tunisie_entreprises.entities import Entreprise, Etablissement


# ===========================================================================
# NIVEAU ÉTABLISSEMENT — calcul unitaire
# ===========================================================================


class est_exonere_tcl(Variable):
    value_type = bool
    entity = Etablissement
    definition_period = YEAR
    label = "L'établissement est-il exonéré de TCL ?"
    reference = "Art. 45 loi 97-11 (exonérations : agriculture, pêche artisanale, etc.)"


class tcl_etablissement_avant_minimum(Variable):
    value_type = float
    unit = "currency"
    entity = Etablissement
    definition_period = YEAR
    label = "TCL brute de l'établissement avant application du minimum légal (CA local × 0,2 %)"
    reference = "Art. 45 loi 97-11 ; paramètre taxes_entreprises.tcl.taux"

    def formula(etablissement, period, parameters):
        ca_local = etablissement("chiffre_affaires_local_etablissement", period)
        taux = parameters(period).taxes_entreprises.tcl.taux
        return ca_local * taux


class tcl_etablissement(Variable):
    value_type = float
    unit = "currency"
    entity = Etablissement
    definition_period = YEAR
    label = "TCL due par l'établissement = max(TCL brute, minimum légal), sauf exonération"
    reference = "Art. 45 loi 97-11 ; paramètre taxes_entreprises.tcl.minimum_annuel"

    def formula(etablissement, period, parameters):
        exonere = etablissement("est_exonere_tcl", period)
        tcl_brute = etablissement("tcl_etablissement_avant_minimum", period)
        minimum = parameters(period).taxes_entreprises.tcl.minimum_annuel
        tcl_avec_minimum = np.maximum(tcl_brute, minimum)
        return np.where(exonere, 0.0, tcl_avec_minimum)


# ===========================================================================
# NIVEAU ENTREPRISE — agrégation
# ===========================================================================


class tcl(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "TCL totale de l'entreprise = somme des TCL de tous ses établissements"
    reference = "Art. 45 loi 97-11"

    def formula(entreprise, period):
        tcl_etab = entreprise.members("tcl_etablissement", period)
        return entreprise.sum(tcl_etab)


class tcl_comptabilisee(Variable):
    value_type = float
    unit = "currency"
    entity = Entreprise
    definition_period = YEAR
    label = "TCL comptabilisée en charges d'exploitation (compte 638)"
    reference = "NCT 03 ; loi 97-11"

    def formula(entreprise, period):
        return entreprise("tcl", period)


# ===========================================================================
# RATIOS DE CONTRÔLE
# ===========================================================================


class taux_effectif_tcl(Variable):
    value_type = float
    entity = Entreprise
    definition_period = YEAR
    label = "Taux effectif TCL (TCL totale / CA local entreprise)"

    def formula(entreprise, period):
        tcl_totale = entreprise("tcl", period)
        ca_local = entreprise("chiffre_affaires_local", period)
        return tcl_totale / (ca_local + (ca_local == 0))
