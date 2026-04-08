"""Système socio-fiscal tunisien — fiscalité des entreprises."""

import os

from openfisca_core.taxbenefitsystems import TaxBenefitSystem

from openfisca_tunisie_entreprises import entities


COUNTRY_DIR = os.path.dirname(os.path.abspath(__file__))


class TunisieEntreprisesTaxBenefitSystem(TaxBenefitSystem):
    """Système OpenFisca pour la fiscalité des entreprises en Tunisie.

    Couvre :
    - IS  : Impôt sur les Sociétés (taux variable selon le secteur)
    - TCL : Taxe sur les établissements à caractère industriel, commercial ou professionnel
    - TFP : Taxe de Formation Professionnelle
    - FOPROLOS : Fonds de Promotion des Logements pour les Salariés
    - Retenues à la source
    - Avantages fiscaux à l'investissement
    """

    CURRENCY = "DT"  # Dinar tunisien (code ISO : TND)

    def __init__(self):
        super().__init__(entities.entities)
        self.add_variables_from_directory(os.path.join(COUNTRY_DIR, "variables"))
        self.load_parameters(os.path.join(COUNTRY_DIR, "parameters"))
