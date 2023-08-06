import astropixie.catalog_service
import astropixie.sample_catalog_provider

from . import data

def hello_universe():
    return "Hello universe!"


provider = astropixie.sample_catalog_provider.SampleCatalogProvider()
Catalog = astropixie.catalog_service.CatalogService(provider)
