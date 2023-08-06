from django.db import models
from mezzanine.pages.models import Page
from django.utils.translation import ugettext_lazy as _, ugettext

class MenuPlaceholder(Page):
    """
    This represents menu items that are placeholders, but do not actually
    represent real pages.
    """

    class Meta:
        verbose_name = _("Menu placeholder")
        verbose_name_plural = _("Menu placeholders")
