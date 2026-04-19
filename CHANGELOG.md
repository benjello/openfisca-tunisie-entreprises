# Changelog

## 0.2.0

* Amélioration technique.
* Périodes concernées : aucune.
* Détails :
  - Ajout d'openfisca-ai comme dépendance dev pour la validation et l'audit.
  - Ajout de workflows CI : validation openfisca-ai, review IA multi-provider, changelog automatique.
  - Ajout de la configuration MCP (`.mcp.json`) pour Claude Code, Cursor, Gemini, etc.
  - Ajout de templates GitLab (issue bug/feature, merge request) en français.
  - Passage du guide de contribution (`CONTRIBUTING.md`) en français avec sections uv, pre-commit, openfisca-ai.
  - Ajout de la validation openfisca-ai dans la checklist du template PR GitHub.
  - Reformatage du code Python avec ruff.

## 0.1.2 - [#2](https://github.com/benjello/openfisca-tunisie-entreprises/pull/2)

* Amélioration technique.
* Périodes concernées : aucune.
* Détails :
  - Ajout de la permission `contents: write` sur le job CI de déploiement pour autoriser la publication du tag git.

## 0.1.1 - [#2](https://github.com/benjello/openfisca-tunisie-entreprises/pull/2)

* Amélioration technique.
* Périodes concernées : aucune.
* Détails :
  - Configuration de ruff pour exclure le répertoire `.github`.
  - Ajout d'un hook pre-push et configuration de la CI.

## 0.1.0 - [#1](https://github.com/benjello/openfisca-tunisie-entreprises/pull/1)

* Amélioration technique.
* Périodes concernées : aucune.
* Détails :
  - Version initiale du paquet OpenFisca Tunisie Entreprises.
  - Implémentation de l'IS, TCL, TFP et FOPROLOS.
