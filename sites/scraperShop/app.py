
from oscar.app import Shop

from apps.catalogue.app import application as catalogue_app

class BaseApplication(Shop):
    catalogue_app = catalogue_app
application = BaseApplication()
