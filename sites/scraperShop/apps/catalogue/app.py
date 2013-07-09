
from apps.catalogue import views
from oscar.apps.catalogue.app import CatalogueApplication as Application


class BaseCatalogueApplication(Application):
    detail_view = views.ProductDetailView


application = BaseCatalogueApplication()
