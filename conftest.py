"""Pytest configuration for OpenFisca Tunisia Entreprises tests."""

from openfisca_core.tools.test_runner import OpenFiscaPlugin

from openfisca_tunisie_entreprises import CountryTaxBenefitSystem


def pytest_configure(config):
    """Register the OpenFisca plugin for the Tunisia entreprises tax system.

    This hook is called by pytest before running tests. It registers an
    OpenFiscaPlugin instance using CountryTaxBenefitSystem so that variables,
    parameters, and benefit rules defined by this package are available to
    the test runner.
    """
    config.pluginmanager.register(OpenFiscaPlugin(CountryTaxBenefitSystem(), {}))
