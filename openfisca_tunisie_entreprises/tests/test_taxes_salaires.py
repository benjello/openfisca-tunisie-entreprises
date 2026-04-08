"""Tests TFP et FOPROLOS.

Valide :
  1. Taux TFP industrie (1 %) vs autres secteurs (2 %)
  2. Déduction formation sur TFP brute
  3. TFP nette = max(TFP brute − formation, 0)
  4. FOPROLOS = 1 % masse salariale
  5. Total taxes assises sur salaires
"""

from openfisca_core.simulation_builder import SimulationBuilder

from openfisca_tunisie_entreprises.tunisie_entreprises_taxbenefitsystem import (
    TunisieEntreprisesTaxBenefitSystem,
)


def make_simulation(period="2023", **variables_entreprise):
    tbs = TunisieEntreprisesTaxBenefitSystem()
    sb = SimulationBuilder()
    entreprise_dict = {"siege_social": ["etab_1"]}
    for var_name, value in variables_entreprise.items():
        entreprise_dict[var_name] = {period: value}
    return sb.build_from_entities(tbs, {
        "etablissements": {"etab_1": {}},
        "entreprises": {"ent_1": entreprise_dict},
    })


MASSE_SALARIALE = 500_000.0  # DT


# ---------------------------------------------------------------------------
# Taux TFP
# ---------------------------------------------------------------------------


def test_tfp_taux_industrie():
    """Secteur industriel → taux 1 %."""
    sim = make_simulation(
        masse_salariale_brute=MASSE_SALARIALE,
        secteur_activite=1,  # industries_manufacturieres
    )
    taux = sim.calculate("taux_tfp", "2023")
    assert abs(taux[0] - 0.01) < 1e-6


def test_tfp_taux_services():
    """Secteur services → taux 2 %."""
    sim = make_simulation(
        masse_salariale_brute=MASSE_SALARIALE,
        secteur_activite=4,  # services
    )
    taux = sim.calculate("taux_tfp", "2023")
    assert abs(taux[0] - 0.02) < 1e-6


# ---------------------------------------------------------------------------
# TFP brute
# ---------------------------------------------------------------------------


def test_tfp_brute_industrie():
    """TFP brute industrie = 500 000 × 1 % = 5 000 DT."""
    sim = make_simulation(
        masse_salariale_brute=MASSE_SALARIALE,
        secteur_activite=1,
    )
    tfp_b = sim.calculate("tfp_brute", "2023")
    assert abs(tfp_b[0] - 5_000.0) < 1.0


def test_tfp_brute_commerce():
    """TFP brute commerce = 500 000 × 2 % = 10 000 DT."""
    sim = make_simulation(
        masse_salariale_brute=MASSE_SALARIALE,
        secteur_activite=3,  # commerce
    )
    tfp_b = sim.calculate("tfp_brute", "2023")
    assert abs(tfp_b[0] - 10_000.0) < 1.0


# ---------------------------------------------------------------------------
# Déduction formation et TFP nette
# ---------------------------------------------------------------------------


def test_deduction_formation_plafonnee():
    """Les dépenses de formation sont plafonnées à la TFP brute."""
    sim = make_simulation(
        masse_salariale_brute=MASSE_SALARIALE,
        secteur_activite=1,            # industrie → TFP brute = 5 000
        depenses_formation_engagees=8_000.0,  # > TFP brute
    )
    ded = sim.calculate("depenses_formation_deductibles", "2023")
    assert abs(ded[0] - 5_000.0) < 1.0, "Déduction doit être plafonnée à la TFP brute"


def test_tfp_nette_avec_formation_partielle():
    """TFP nette = TFP brute − dépenses formation (si dépenses < TFP brute)."""
    sim = make_simulation(
        masse_salariale_brute=MASSE_SALARIALE,
        secteur_activite=1,             # TFP brute = 5 000
        depenses_formation_engagees=2_000.0,
    )
    tfp_n = sim.calculate("tfp_nette", "2023")
    assert abs(tfp_n[0] - 3_000.0) < 1.0


def test_tfp_nette_formation_couvre_tout():
    """TFP nette = 0 si les dépenses de formation couvrent toute la TFP brute."""
    sim = make_simulation(
        masse_salariale_brute=MASSE_SALARIALE,
        secteur_activite=1,             # TFP brute = 5 000
        depenses_formation_engagees=5_000.0,
    )
    tfp_n = sim.calculate("tfp_nette", "2023")
    assert tfp_n[0] == 0.0


# ---------------------------------------------------------------------------
# FOPROLOS
# ---------------------------------------------------------------------------


def test_foprolos():
    """FOPROLOS = 500 000 × 1 % = 5 000 DT."""
    sim = make_simulation(masse_salariale_brute=MASSE_SALARIALE)
    fp = sim.calculate("foprolos", "2023")
    assert abs(fp[0] - 5_000.0) < 1.0


# ---------------------------------------------------------------------------
# Total taxes assises sur salaires
# ---------------------------------------------------------------------------


def test_total_taxes_salaires():
    """Industrie, sans formation : TFP nette 5 000 + FOPROLOS 5 000 = 10 000 DT."""
    sim = make_simulation(
        masse_salariale_brute=MASSE_SALARIALE,
        secteur_activite=1,
    )
    total = sim.calculate("taxes_assises_salaires", "2023")
    assert abs(total[0] - 10_000.0) < 1.0
