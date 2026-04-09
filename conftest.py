from openfisca_core.tools.test_runner import OpenFiscaPlugin
from openfisca_tunisie_entreprises import CountryTaxBenefitSystem


def pytest_configure(config):
    config.pluginmanager.register(OpenFiscaPlugin(CountryTaxBenefitSystem(), {}))
