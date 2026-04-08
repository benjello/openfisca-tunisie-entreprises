"""Tests de la chaîne de calcul IS — cas simples.

Utilisation : pytest openfisca_tunisie_entreprises/tests/test_is.py

Ces tests valident la logique de calcul pas à pas :
  1. Taux IS par catégorie (normal 15 %, majoré 35 %, réduit 10 %)
  2. TMI (0,2 % du CA brut)
  3. Résultat fiscal (résultat comptable + réintégrations − déductions)
  4. IS net dû (max IS brut, TMI)
  5. Solde IS à payer (IS dû − acomptes)
"""

from openfisca_core.simulation_builder import SimulationBuilder

from openfisca_tunisie_entreprises.tunisie_entreprises_taxbenefitsystem import (
    TunisieEntreprisesTaxBenefitSystem,
)


def make_simulation(period="2023", **variables_entreprise):
    """Crée une simulation avec une seule entreprise (siège = 1 établissement)."""
    tbs = TunisieEntreprisesTaxBenefitSystem()
    sb = SimulationBuilder()
    entreprise_dict = {"siege_social": ["etab_1"]}
    for var_name, value in variables_entreprise.items():
        entreprise_dict[var_name] = {period: value}
    return sb.build_from_entities(tbs, {
        "etablissements": {"etab_1": {}},
        "entreprises": {"ent_1": entreprise_dict},
    })


# ---------------------------------------------------------------------------
# Taux IS
# ---------------------------------------------------------------------------


def test_taux_is_normal():
    """Une SARL de droit commun paie 15 % depuis 2021."""
    sim = make_simulation(period="2023", categorie_is=1)  # 1 = normal
    taux = sim.calculate("taux_is_applicable", "2023")
    assert abs(taux[0] - 0.15) < 1e-6, f"Attendu 0.15, obtenu {taux[0]}"


def test_taux_is_majore():
    """Une banque paie 35 %."""
    sim = make_simulation(period="2023", categorie_is=0)  # 0 = majore
    taux = sim.calculate("taux_is_applicable", "2023")
    assert abs(taux[0] - 0.35) < 1e-6, f"Attendu 0.35, obtenu {taux[0]}"


def test_taux_is_reduit():
    """Une entreprise individuelle paie 10 % depuis 2021."""
    sim = make_simulation(period="2023", categorie_is=2)  # 2 = reduit
    taux = sim.calculate("taux_is_applicable", "2023")
    assert abs(taux[0] - 0.10) < 1e-6, f"Attendu 0.10, obtenu {taux[0]}"


# ---------------------------------------------------------------------------
# Résultat fiscal
# ---------------------------------------------------------------------------


def test_resultat_fiscal_avec_reintegrations():
    """Résultat fiscal = résultat comptable + réintégrations − déductions."""
    sim = make_simulation(
        period="2023",
        resultat_avant_impot=100_000.0,          # bénéfice comptable
        reintegration_amendes_penalites=5_000.0,  # amendes non déductibles
        deduction_dividendes_participation=8_000.0,  # dividendes exonérés
    )
    rf = sim.calculate("resultat_fiscal", "2023")
    assert abs(rf[0] - 97_000.0) < 1.0, f"Attendu 97000, obtenu {rf[0]}"


def test_resultat_fiscal_deficitaire_plancher_zero():
    """Un résultat fiscal négatif est ramené à zéro (le déficit n'est pas imposé)."""
    sim = make_simulation(
        period="2023",
        resultat_avant_impot=-20_000.0,  # perte comptable
    )
    rf = sim.calculate("resultat_fiscal", "2023")
    assert rf[0] == 0.0, f"Attendu 0, obtenu {rf[0]}"


# ---------------------------------------------------------------------------
# IS brut et TMI
# ---------------------------------------------------------------------------


def test_is_brut_taux_normal():
    """IS brut = résultat fiscal × 15 % (catégorie normale, exercice 2023)."""
    sim = make_simulation(
        period="2023",
        resultat_avant_impot=200_000.0,
        categorie_is=1,  # normal
    )
    is_b = sim.calculate("is_brut", "2023")
    assert abs(is_b[0] - 30_000.0) < 1.0, f"Attendu 30000, obtenu {is_b[0]}"


def test_tmi_sur_ca():
    """TMI = CA brut × 0,2 %."""
    sim = make_simulation(
        period="2023",
        chiffre_affaires_local=5_000_000.0,
    )
    tmi_v = sim.calculate("tmi", "2023")
    assert abs(tmi_v[0] - 10_000.0) < 1.0, f"Attendu 10000, obtenu {tmi_v[0]}"


def test_is_du_applique_tmi_si_superieur():
    """Si la TMI > IS brut et que la TMI est applicable, c'est la TMI qui s'applique."""
    # CA = 5 000 000 DT → TMI = 10 000 DT
    # Résultat fiscal = 20 000 DT → IS brut (15 %) = 3 000 DT
    # IS dû = max(3 000, 10 000) = 10 000 DT
    sim = make_simulation(
        period="2023",
        chiffre_affaires_local=5_000_000.0,
        resultat_avant_impot=20_000.0,
        categorie_is=1,
        annees_activite=10,   # TMI applicable (> 5 ans)
        est_exonere_is=False,
    )
    is_du = sim.calculate("is_du_avant_degrevement", "2023")
    assert abs(is_du[0] - 10_000.0) < 1.0, f"Attendu 10000, obtenu {is_du[0]}"


# ---------------------------------------------------------------------------
# Acomptes et solde
# ---------------------------------------------------------------------------


def test_solde_is_a_payer():
    """Solde IS = IS net dû − acomptes payés (3 × 30 % de l'IS N-1)."""
    # IS N-1 = 30 000 DT → acomptes = 3 × 30 % × 30 000 = 27 000 DT
    # IS dû cette année = 40 000 DT → solde = 40 000 − 27 000 = 13 000 DT
    sim = make_simulation(
        period="2023",
        resultat_avant_impot=266_667.0,  # ≈ 40 000 / 0,15
        categorie_is=1,
        annees_activite=10,
        est_exonere_is=False,
        is_exercice_precedent=30_000.0,
    )
    solde = sim.calculate("solde_is_a_payer", "2023")
    # IS dû ≈ 40 000, acomptes = 27 000, solde ≈ 13 000
    assert solde[0] > 0, "Le solde devrait être positif (IS à payer)"
