"""Tests TCL — Taxe sur les établissements à caractère industriel, commercial ou professionnel.

Valide :
  1. TCL brute = CA local × 0,2 %
  2. Application du minimum légal (100 DT)
  3. Exonération de TCL
  4. Agrégation multi-établissements au niveau entreprise
"""

from openfisca_core.simulation_builder import SimulationBuilder

from openfisca_tunisie_entreprises.tunisie_entreprises_taxbenefitsystem import (
    TunisieEntreprisesTaxBenefitSystem,
)


def make_simulation_mono(period="2023", **vars_etab):
    """Simulation avec une entreprise (siège social = 1 établissement)."""
    tbs = TunisieEntreprisesTaxBenefitSystem()
    sb = SimulationBuilder()
    etab_dict = {}
    for k, v in vars_etab.items():
        etab_dict[k] = {period: v}
    return sb.build_from_entities(tbs, {
        "etablissements": {"etab_1": etab_dict},
        "entreprises": {"ent_1": {"siege_social": ["etab_1"]}},
    })


def make_simulation_multi(period="2023", ca_locaux=None, exoneres=None):
    """Simulation avec une entreprise et plusieurs établissements.

    ca_locaux : liste des CA locaux par établissement (DT)
    exoneres  : liste de booléens (exonération TCL par établissement)
    """
    ca_locaux = ca_locaux or [0.0]
    exoneres = exoneres or [False] * len(ca_locaux)
    n = len(ca_locaux)
    etab_ids = [f"etab_{i}" for i in range(n)]

    etablissements = {
        etab_ids[i]: {
            "chiffre_affaires_local_etablissement": {period: ca_locaux[i]},
            "est_exonere_tcl": {period: exoneres[i]},
        }
        for i in range(n)
    }
    entreprise_dict = {"siege_social": [etab_ids[0]]}
    if n > 1:
        entreprise_dict["etablissements_secondaires"] = etab_ids[1:]

    tbs = TunisieEntreprisesTaxBenefitSystem()
    sb = SimulationBuilder()
    return sb.build_from_entities(tbs, {
        "etablissements": etablissements,
        "entreprises": {"ent_1": entreprise_dict},
    })


# ---------------------------------------------------------------------------
# TCL brute (avant minimum)
# ---------------------------------------------------------------------------


def test_tcl_brute_taux():
    """TCL brute = CA local × 0,2 %."""
    # CA local = 1 000 000 DT → TCL brute = 2 000 DT
    sim = make_simulation_mono(chiffre_affaires_local_etablissement=1_000_000.0)
    tcl_b = sim.calculate("tcl_etablissement_avant_minimum", "2023")
    assert abs(tcl_b[0] - 2_000.0) < 1.0


# ---------------------------------------------------------------------------
# Minimum légal (100 DT)
# ---------------------------------------------------------------------------


def test_tcl_minimum_applique():
    """Si CA local très faible, le minimum de 100 DT s'applique."""
    # CA local = 10 000 DT → TCL brute = 20 DT < 100 DT → TCL due = 100 DT
    sim = make_simulation_mono(chiffre_affaires_local_etablissement=10_000.0)
    tcl_due = sim.calculate("tcl_etablissement", "2023")
    assert abs(tcl_due[0] - 100.0) < 1.0, f"Attendu 100, obtenu {tcl_due[0]}"


def test_tcl_pas_de_minimum_si_superieur():
    """Si TCL brute > minimum, le minimum ne s'applique pas."""
    # CA local = 1 000 000 DT → TCL brute = 2 000 DT > 100 DT → TCL due = 2 000 DT
    sim = make_simulation_mono(chiffre_affaires_local_etablissement=1_000_000.0)
    tcl_due = sim.calculate("tcl_etablissement", "2023")
    assert abs(tcl_due[0] - 2_000.0) < 1.0


# ---------------------------------------------------------------------------
# Exonération
# ---------------------------------------------------------------------------


def test_tcl_exoneration():
    """Un établissement exonéré ne paie pas la TCL, même si CA > 0."""
    sim = make_simulation_mono(
        chiffre_affaires_local_etablissement=500_000.0,
        est_exonere_tcl=True,
    )
    tcl_due = sim.calculate("tcl_etablissement", "2023")
    assert tcl_due[0] == 0.0


# ---------------------------------------------------------------------------
# Agrégation multi-établissements
# ---------------------------------------------------------------------------


def test_tcl_agregation_deux_etablissements():
    """TCL entreprise = somme des TCL des établissements.

    Étab 1 : CA 500 000 DT → TCL 1 000 DT
    Étab 2 : CA 200 000 DT → TCL   400 DT
    Total   :                       1 400 DT
    """
    sim = make_simulation_multi(ca_locaux=[500_000.0, 200_000.0])
    tcl_totale = sim.calculate("tcl", "2023")
    assert abs(tcl_totale[0] - 1_400.0) < 1.0


def test_tcl_agregation_avec_exoneration():
    """Un établissement exonéré ne contribue pas au total entreprise.

    Étab 1 : CA 500 000 DT, exonéré → TCL 0 DT
    Étab 2 : CA 200 000 DT          → TCL 400 DT
    Total   :                             400 DT
    """
    sim = make_simulation_multi(
        ca_locaux=[500_000.0, 200_000.0],
        exoneres=[True, False],
    )
    tcl_totale = sim.calculate("tcl", "2023")
    assert abs(tcl_totale[0] - 400.0) < 1.0


def test_tcl_agregation_minimum_par_etablissement():
    """Le minimum de 100 DT s'applique par établissement, pas globalement.

    Étab 1 : CA 1 000 DT → TCL brute 2 DT < 100 DT → TCL 100 DT
    Étab 2 : CA 5 000 DT → TCL brute 10 DT < 100 DT → TCL 100 DT
    Total   :                                           200 DT
    """
    sim = make_simulation_multi(ca_locaux=[1_000.0, 5_000.0])
    tcl_totale = sim.calculate("tcl", "2023")
    assert abs(tcl_totale[0] - 200.0) < 1.0
