"""Tests des retenues à la source.

Valide :
  1. RS honoraires PM (3 %)
  2. RS loyers PM (15 %) et PP (15 %)
  3. RS dividendes (10 % depuis 2021)
  4. RS marchés État (3 %)
  5. Total RS collectées
  6. RS subies imputable sur IS
  7. Solde IS final (IS net − RS subies − acomptes)
"""

from openfisca_core.simulation_builder import SimulationBuilder

from openfisca_tunisie_entreprises.tunisie_entreprises_taxbenefitsystem import (
    TunisieEntreprisesTaxBenefitSystem,
)

PERIOD = "2023"


def make_sim(**vars_entreprise):
    tbs = TunisieEntreprisesTaxBenefitSystem()
    sb = SimulationBuilder()
    entreprise_dict = {"siege_social": ["etab_1"]}
    for k, v in vars_entreprise.items():
        entreprise_dict[k] = {PERIOD: v}
    return sb.build_from_entities(tbs, {
        "etablissements": {"etab_1": {}},
        "entreprises": {"ent_1": entreprise_dict},
    })


# ---------------------------------------------------------------------------
# Côté débiteur — RS collectées
# ---------------------------------------------------------------------------


def test_rs_honoraires_pm():
    """RS honoraires PM = 100 000 × 3 % = 3 000 DT."""
    sim = make_sim(honoraires_verses_pm=100_000.0)
    rs = sim.calculate("rs_honoraires_verses", PERIOD)
    assert abs(rs[0] - 3_000.0) < 1.0


def test_rs_loyers_pm():
    """RS loyers PM = 50 000 × 15 % = 7 500 DT."""
    sim = make_sim(loyers_verses_pm=50_000.0)
    rs = sim.calculate("rs_loyers_verses_pm", PERIOD)
    assert abs(rs[0] - 7_500.0) < 1.0


def test_rs_loyers_pp():
    """RS loyers PP = 30 000 × 15 % = 4 500 DT."""
    sim = make_sim(loyers_verses_pp=30_000.0)
    rs = sim.calculate("rs_loyers_verses_pp", PERIOD)
    assert abs(rs[0] - 4_500.0) < 1.0


def test_rs_dividendes_2023():
    """RS dividendes 2023 = 200 000 × 10 % = 20 000 DT (taux LF 2021)."""
    sim = make_sim(dividendes_distribues=200_000.0)
    rs = sim.calculate("rs_dividendes", PERIOD)
    assert abs(rs[0] - 20_000.0) < 1.0


def test_rs_marches_etat():
    """RS marchés État = 500 000 × 3 % = 15 000 DT."""
    sim = make_sim(marches_etat_verses=500_000.0)
    rs = sim.calculate("rs_marches_etat", PERIOD)
    assert abs(rs[0] - 15_000.0) < 1.0


def test_total_rs_collectees():
    """Total RS = somme de toutes les RS collectées."""
    sim = make_sim(
        honoraires_verses_pm=100_000.0,   # → 3 000
        loyers_verses_pm=50_000.0,        # → 7 500
        loyers_verses_pp=30_000.0,        # → 4 500
        dividendes_distribues=200_000.0,  # → 20 000
        marches_etat_verses=500_000.0,    # → 15 000
    )
    total = sim.calculate("total_rs_collectees", PERIOD)
    assert abs(total[0] - 50_000.0) < 1.0


# ---------------------------------------------------------------------------
# Côté créditeur — RS subies (imputable sur IS)
# ---------------------------------------------------------------------------


def test_rs_subies_imputable():
    """Total RS subies = somme des RS reçues."""
    sim = make_sim(
        rs_subies_honoraires=5_000.0,
        rs_subies_loyers=10_000.0,
        rs_subies_marches=3_000.0,
    )
    total = sim.calculate("total_rs_subies", PERIOD)
    assert abs(total[0] - 18_000.0) < 1.0


# ---------------------------------------------------------------------------
# Solde IS final
# ---------------------------------------------------------------------------


def test_solde_is_final():
    """Solde IS final = IS net − RS subies − acomptes.

    IS net (hypothèse) = 40 000 DT
    RS subies          =  5 000 DT
    Acomptes (IS N-1 = 30 000 → 3 × 30 % = 27 000 DT)
    Solde              = 40 000 − 5 000 − 27 000 = 8 000 DT
    """
    sim = make_sim(
        # IS net ≈ 40 000 : résultat fiscal ≈ 266 667 × 15 %
        resultat_avant_impot=266_667.0,
        categorie_is=1,  # 15 %
        annees_activite=10,
        est_exonere_is=False,
        is_exercice_precedent=30_000.0,   # acomptes = 27 000
        rs_subies_honoraires=5_000.0,     # RS subies
    )
    solde = sim.calculate("solde_is_final", PERIOD)
    # IS net ≈ 40 000 ; acomptes = 27 000 ; RS subies = 5 000 → solde ≈ 8 000
    assert solde[0] > 0, "Solde doit être positif (IS à payer)"
    assert abs(solde[0] - 8_000.0) < 100.0  # marge arrondi


def test_solde_is_final_credit():
    """Si RS subies + acomptes > IS net → crédit IS (solde négatif)."""
    sim = make_sim(
        resultat_avant_impot=50_000.0,
        categorie_is=1,  # IS net = 7 500
        annees_activite=10,
        est_exonere_is=False,
        is_exercice_precedent=40_000.0,   # acomptes = 36 000 > IS net
        rs_subies_honoraires=5_000.0,
    )
    solde = sim.calculate("solde_is_final", PERIOD)
    assert solde[0] < 0, "Solde doit être négatif (crédit IS restituable)"
