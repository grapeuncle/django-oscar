from decimal import Decimal as D
import datetime

from oscar.apps.dashboard.reports.csv_utils import CsvUnicodeReader
from oscar.apps.catalogue import models, categories
from oscar.apps.partner import models as partner_models


class Importer(object):
    """
    Quick and dirty catalogue importer
    """

    def __init__(self, logger):
        self.logger = logger

    def handle(self, product_class_name, filepath):
        product_class = models.ProductClass.objects.get(
            name=product_class_name)

        for row in CsvUnicodeReader(open(filepath, 'r'), quotechar='"'):
            if row[0] == 'category':
                attribute_codes = row[5:]
                continue
            self.create_product(product_class, attribute_codes,  row)

    def create_product(self, product_class, attribute_codes, row):
        category, upc, title, description, price = row[0:5]

        # Create product
        if upc:
            try:
                product = models.Product.objects.get(
                    upc=upc)
            except models.Product.DoesNotExist:
                product = models.Product(upc=upc)
        else:
            product = models.Product()

        product.title = title
        product.description = description
        product.product_class = product_class
        product.price = D(price)

        # Attributes
        for code, value in zip(attribute_codes, row[5:]):
            setattr(product.attr, code, value)

        product.save()

        # Category information
        if category:
            leaf = categories.create_from_breadcrumbs(category)
            models.ProductCategory.objects.get_or_create(
                product=product, category=leaf)

  
