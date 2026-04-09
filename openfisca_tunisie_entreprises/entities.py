"""Entités du modèle de fiscalité des entreprises en Tunisie.

Deux entités sont définies :
- Entreprise  : l'unité légale (identifiée par son matricule fiscal).
                C'est à ce niveau qu'est calculé l'IS.
- Etablissement : chaque établissement composant l'entreprise.
                  C'est à ce niveau qu'est calculée la TCL.

Voir : https://openfisca.org/doc/coding-the-legislation/50_entities.html
"""

from openfisca_core.entities import build_entity

Entreprise = build_entity(
    key="entreprise",
    plural="entreprises",
    label="Entreprise (unité légale)",
    doc="""
    Personne morale ou physique soumise à l'IS ou à l'IR dans la catégorie BIC/BNC/BEAP.
    Identifiée par son matricule fiscal tunisien.

    Une entreprise regroupe un ou plusieurs établissements.
    Le siège social est l'établissement principal (rôle unique).
    """,
    roles=[
        {
            "key": "siege_social",
            "plural": "siege_social",
            "label": "Siège social",
            "max": 1,
            "doc": "L'établissement siège, unique au sein de l'entreprise.",
        },
        {
            "key": "etablissement_secondaire",
            "plural": "etablissements_secondaires",
            "label": "Établissements secondaires",
            "doc": "Les autres établissements rattachés à la même unité légale.",
        },
    ],
)

Etablissement = build_entity(
    key="etablissement",
    plural="etablissements",
    label="Établissement",
    doc="""
    Unité locale d'activité économique.
    C'est à ce niveau qu'est assise la TCL (Taxe sur les établissements
    à caractère industriel, commercial ou professionnel).

    Chaque établissement appartient à une Entreprise via un rôle
    (siege_social ou etablissement_secondaire).
    """,
    is_person=True,
)

entities = [Entreprise, Etablissement]
