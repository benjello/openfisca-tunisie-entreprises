# Contributing to OpenFisca Tunisie Entreprises

Thank you for wanting to contribute to OpenFisca! :smiley:

TL;DR: [GitHub Flow](https://guides.github.com/introduction/flow/), [SemVer](http://semver.org/).

## Pull requests

We follow the [GitHub Flow](https://guides.github.com/introduction/flow/): all code contributions are submitted via a pull request towards the `main` branch.

Opening a Pull Request means you want that code to be merged. If you want to only discuss it, send a link to your branch along with your questions through whichever communication channel you prefer.

### Peer reviews

All pull requests must be reviewed by someone else than their original author.

> In case of a lack of available reviewers, one may review oneself, but only after at least 24 hours have passed without working on the code to review.

To help reviewers, make sure to add to your PR a **clear text explanation** of your changes.

In case of breaking changes, you **must** give details about what features were deprecated.

> You must also provide guidelines to help users adapt their code to be compatible with the new version of the package.

## Advertising changes

### Version number

We follow the [semantic versioning](http://semver.org/) spec: any change impacts the version number, and the version number conveys API compatibility information **only**.

Examples:

#### Patch bump

- Fixing or improving an already existing calculation.

#### Minor bump

- Adding a variable to the tax and benefit system.

#### Major bump

- Renaming or removing a variable from the tax and benefit system.

### Changelog

OpenFisca Tunisie Entreprises changes must be understood by users who don't necessarily work on the code. The CHANGELOG must therefore be as explicit as possible.

Each change must be documented with the following elements:

- On the first line appears as a title the version number, as well as a link towards the Pull Request introducing the change. The title level must match the incrementation level of the version.

  > For instance :
  > # 2.0.0 [#10](https://github.com/benjello/openfisca-tunisie-entreprises/pull/10)
  >
  > ## 1.2.0 [#8](https://github.com/benjello/openfisca-tunisie-entreprises/pull/8)
  >
  > ### 1.1.5 [#5](https://github.com/benjello/openfisca-tunisie-entreprises/pull/5)

- The second line indicates the type of the change. The possible types are:
  - `Évolution du système socio-fiscal` : Amélioration, correction ou mise à jour de calcul.
  - `Amélioration technique` : Amélioration des performances, changement du processus d'installation, changement de syntaxe de formule…
  - `Correction de crash` : Impact tous les réutilisateurs.
  - `Changement mineur` : Refactoring, métadonnées…

- In the case of a `Évolution du système socio-fiscal`, the following elements must then be specified:
  - The periods impacted by the change.
  - The tax and benefit system areas impacted by the change.

- Finally, for all cases except `Changement mineur`, the changes must be explained by details given from a user perspective.

## Branch protection and CI

When the supported Python versions (or other CI matrix) change in `.github/workflows/workflow.yml`, update the repository's **Required status checks** so GitHub no longer expects obsolete jobs:

1. Open **Settings** → **Branches** → branch protection rule for `main`.
2. In **Require status checks to pass before merging**, remove any checks that no longer exist (e.g. `build (3.9, ubuntu-24.04)`).
3. After the next run of the new workflow, add the new job names if you want them to be required.
