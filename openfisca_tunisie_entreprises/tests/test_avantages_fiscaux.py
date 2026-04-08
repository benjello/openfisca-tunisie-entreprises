"""Tests des avantages fiscaux à l'investissement.

Valide :
  1. Exonération IS totale ETE (10 premières années)
  2. Régime ETE désactivé après 10 ans
  3. Exonération IS zone de développement régional (5 ans zone 1, 10 ans zone 2)
  4. Déduction supplémentaire après période d'exonération (25 % zone 1, 50 % zone 2)
  5. Déduction pour réinvestissement (35 % du montant réinvesti, plafonnée au bénéfice)
  6. IS net après avantages
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
# Entreprises totalement exportatrices (ETE)
# ---------------------------------------------------------------------------


def test_ete_exoneration_pendant_10_ans():
    """ETE en année 5 → IS brut entièrement exonéré."""
    sim = make_sim(
        est_totalement_exportatrice=True,
        annees_dans_regime_ete=5,
        resultat_avant_impot=300_000.0,
        categorie_is=1,  # normal 15 % → IS brut = 45 000
    )
    exon = sim.calculate("exoneration_is_ete", PERIOD)
    assert abs(exon[0] - 45_000.0) < 1.0


def test_ete_exoneration_exactement_10_ans():
    """ETE à l'année 10 (incluse) → encore exonérée."""
    sim = make_sim(
        est_totalement_exportatrice=True,
        annees_dans_regime_ete=10,
        resultat_avant_impot=200_000.0,
        categorie_is=1,
    )
    regime = sim.calculate("est_regime_ete_actif", PERIOD)
    assert regime[0]


def test_ete_pas_d_exoneration_apres_10_ans():
    """ETE en année 11 → exonération = 0 DT."""
    sim = make_sim(
        est_totalement_exportatrice=True,
        annees_dans_regime_ete=11,
        resultat_avant_impot=200_000.0,
        categorie_is=1,
    )
    exon = sim.calculate("exoneration_is_ete", PERIOD)
    assert exon[0] == 0.0


def test_non_ete_pas_d_exoneration():
    """Entreprise non ETE → exonération = 0 DT, peu importe les années."""
    sim = make_sim(
        est_totalement_exportatrice=False,
        annees_dans_regime_ete=3,
        resultat_avant_impot=200_000.0,
        categorie_is=1,
    )
    exon = sim.calculate("exoneration_is_ete", PERIOD)
    assert exon[0] == 0.0


# ---------------------------------------------------------------------------
# Zones de développement régional
# ---------------------------------------------------------------------------


def test_zone1_exoneration_5_ans():
    """Zone 1 → 5 ans d'exonération. En année 3 : exonération = IS brut."""
    sim = make_sim(
        zone_developpement_regional=1,
        annees_dans_zone=3,
        resultat_avant_impot=100_000.0,
        categorie_is=1,  # IS brut = 15 000
    )
    exon = sim.calculate("exoneration_is_zone_developpement", PERIOD)
    assert abs(exon[0] - 15_000.0) < 1.0


def test_zone1_pas_exoneration_apres_5_ans():
    """Zone 1 → exonération terminée à l'année 6."""
    sim = make_sim(
        zone_developpement_regional=1,
        annees_dans_zone=6,
        resultat_avant_impot=100_000.0,
        categorie_is=1,
    )
    exon = sim.calculate("exoneration_is_zone_developpement", PERIOD)
    assert exon[0] == 0.0


def test_zone2_exoneration_10_ans():
    """Zone 2 → 10 ans d'exonération. En année 8 : exonérée."""
    sim = make_sim(
        zone_developpement_regional=2,
        annees_dans_zone=8,
        resultat_avant_impot=200_000.0,
        categorie_is=1,  # IS brut = 30 000
    )
    exon = sim.calculate("exoneration_is_zone_developpement", PERIOD)
    assert abs(exon[0] - 30_000.0) < 1.0


def test_zone1_deduction_supplementaire_25_pct():
    """Après exonération zone 1 (année 6+) : déduction supplémentaire = 25 % du bénéfice fiscal."""
    # Bénéfice fiscal = 200 000 → déduction sup = 50 000
    sim = make_sim(
        zone_developpement_regional=1,
        annees_dans_zone=6,
        resultat_avant_impot=200_000.0,
    )
    ded = sim.calculate("deduction_supplementaire_zone", PERIOD)
    assert abs(ded[0] - 50_000.0) < 1.0


def test_zone2_deduction_supplementaire_50_pct():
    """Après exonération zone 2 (année 11+) : déduction supplémentaire = 50 % du bénéfice fiscal."""
    sim = make_sim(
        zone_developpement_regional=2,
        annees_dans_zone=11,
        resultat_avant_impot=200_000.0,
    )
    ded = sim.calculate("deduction_supplementaire_zone", PERIOD)
    assert abs(ded[0] - 100_000.0) < 1.0


# ---------------------------------------------------------------------------
# Déduction pour réinvestissement
# ---------------------------------------------------------------------------


def test_deduction_reinvestissement_35_pct():
    """Déduction = 35 % du montant réinvesti, si < bénéfice net."""
    # Réinvestissement = 100 000 → déduction = 35 000
    # Bénéfice = 200 000 → plafond non atteint
    sim = make_sim(
        souscriptions_capital_societes=100_000.0,
        resultat_avant_impot=200_000.0,
        categorie_is=1,
    )
    ded = sim.calculate("deduction_reinvestissement_base", PERIOD)
    assert abs(ded[0] - 35_000.0) < 1.0


def test_deduction_reinvestissement_plafonnee_au_benefice():
    """Si 35 % du réinvesti > bénéfice net, on plafonne au bénéfice net."""
    # Réinvestissement = 1 000 000 → 35 % = 350 000
    # Bénéfice fiscal = 50 000 → déduction = 50 000
    sim = make_sim(
        souscriptions_capital_societes=1_000_000.0,
        resultat_avant_impot=50_000.0,
        categorie_is=1,
    )
    ded = sim.calculate("deduction_reinvestissement_base", PERIOD)
    assert abs(ded[0] - 50_000.0) < 1.0


# ---------------------------------------------------------------------------
# IS net après avantages
# ---------------------------------------------------------------------------


def test_is_net_apres_exoneration_ete():
    """ETE en période d'exonération → IS net après avantages = 0."""
    sim = make_sim(
        est_totalement_exportatrice=True,
        annees_dans_regime_ete=3,
        resultat_avant_impot=500_000.0,
        categorie_is=1,
        annees_activite=10,
        est_exonere_is=True,  # ETE = exonérée → TMI non applicable
    )
    is_net = sim.calculate("is_net_apres_avantages", PERIOD)
    assert is_net[0] == 0.0
