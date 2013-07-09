from django.conf import settings
from django.http import HttpResponsePermanentRedirect, Http404
from django.views.generic import ListView, DetailView
from django.db.models import get_model
from django.utils.translation import ugettext_lazy as _

from oscar.core.loading import get_class
from oscar.apps.catalogue.signals import product_viewed, product_search

from apps.catalogue import forms
from django.views.generic.edit import FormMixin

Product = get_model('catalogue', 'product')
ProductReview = get_model('reviews', 'ProductReview')
Category = get_model('catalogue', 'category')
ProductAlert = get_model('customer', 'ProductAlert')
ProductAlertForm = get_class('customer.forms', 'ProductAlertForm')


class ProductDetailView(FormMixin, DetailView):
    context_object_name = 'product'
    model = Product
    form_class = forms.GatewayForm
    view_signal = product_viewed
    template_folder = "catalogue"

    def get(self, request, **kwargs):
        # Ensure that the correct URL is used
        product = self.get_object()

        if product.is_variant:
            return HttpResponsePermanentRedirect(product.parent.get_absolute_url())

        correct_path = product.get_absolute_url()
        if correct_path != request.path:
            return HttpResponsePermanentRedirect(correct_path)

        response = super(ProductDetailView, self).get(request, **kwargs)
        self.send_signal(request, response, product)
        return response

    def get_object(self):
        # Use a cached version to prevent unnecessary DB calls
        if not hasattr(self, '_product'):
            setattr(
                self, '_product', super(ProductDetailView, self).get_object())
        return self._product

    def get_context_data(self, **kwargs):
        ctx = super(ProductDetailView, self).get_context_data(**kwargs)
        ctx['reviews'] = self.get_reviews()
        ctx['product'] = self.get_object()
        ctx['alert_form'] = self.get_alert_form()
        ctx['has_active_alert'] = self.get_alert_status()
        form_class = self.get_form_class()
        ctx['form'] = self.get_form(form_class)
        return ctx

    def get_alert_status(self):
        # Check if this user already have an alert for this product
        has_alert = False
        if self.request.user.is_authenticated():
            alerts = ProductAlert.objects.filter(
                product=self.object, user=self.request.user,
                status=ProductAlert.ACTIVE)
            has_alert = alerts.count() > 0
        return has_alert

    def get_alert_form(self):
        return ProductAlertForm(
            user=self.request.user, product=self.object)

    def get_reviews(self):
        return self.object.reviews.filter(status=ProductReview.APPROVED)

    def send_signal(self, request, response, product):
        self.view_signal.send(
            sender=self, product=product, user=request.user, request=request,
            response=response)

    def get_template_names(self):
        """
        Return a list of possible templates.

        We try 2 options before defaulting to catalogue/detail.html:
            1). detail-for-upc-<upc>.html
            2). detail-for-class-<classname>.html

        This allows alternative templates to be provided for a per-product
        and a per-item-class basis.
        """
        product = self.get_object()
        return [
            '%s/detail-for-upc-%s.html' % (
                self.template_folder, product.upc),
            '%s/detail-for-class-%s.html' % (
                self.template_folder, product.get_product_class().name.lower()),
            '%s/detail.html' % (self.template_folder)]


def get_product_base_queryset():
    """
    Return ``QuerySet`` for product model with related
    content pre-loaded. The ``QuerySet`` returns unfiltered
    results for further filtering.
    """
    return Product.browsable.select_related(
        'product_class',
    ).prefetch_related(
        'variants',
        'product_options',
        'product_class__options',
        'stockrecord',
        'images',
    ).all()

