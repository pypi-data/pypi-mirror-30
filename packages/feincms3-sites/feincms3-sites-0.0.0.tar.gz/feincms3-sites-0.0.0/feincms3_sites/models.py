from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class MetaMixin(models.Model):
    sites_title = models.CharField(
        _('title'),
        max_length=200,
        blank=True,
        help_text=_('Used for Open Graph and other sites tags.'),
    )
    sites_description = models.TextField(
        _('description'),
        blank=True,
        help_text=_('Override the description for this page.'),
    )
    sites_image = models.ImageField(
        _('image'),
        blank=True,
        upload_to='sites/%Y/%m',
        help_text=_('Set the Open Graph image.'),
    )
    sites_canonical = models.URLField(
        _('canonical URL'),
        blank=True,
        help_text=_('If you need this you probably know.'),
    )

    class Meta:
        abstract = True

    @classmethod
    def admin_fieldset(cls, **kwargs):
        cfg = {
            'fields': (
                'sites_title', 'sites_description', 'sites_image',
                'sites_canonical',
            ),
            'classes': ('tabbed',),
        }
        cfg.update(kwargs)
        return (_('Meta tags'), cfg)
