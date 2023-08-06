from cms.models import CMSPlugin
from cms.models.fields import PageField
from filer.fields.file import FilerFileField
from djangocms_attributes_field.fields import AttributesField

from django.db import models
from django.utils.translation import ugettext_lazy as _


class SVGPluginModel(CMSPlugin):
    """
    Base SVG plugin model
    """

    file = FilerFileField(
        blank=False, null=False, verbose_name=_('SVG file'),
        help_text=_('Provide an SVG file')
    )

    class Meta:
        abstract = True


class FilerSvgInlinePluginModel(SVGPluginModel):
    """
    An inline SVG image
    """

    def get_svg_code(self):
        try:
            return self.file.file.read()
        except IOError:
            return ''

    def __str__(self):
        return u'Inline SVG'

    class Meta:
        verbose_name = _('Inline SVG image')
        verbose_name_plural = _('Inline SVG images')


class FilerSvgImagePluginModel(SVGPluginModel):
    """
    An SVG image
    """

    LINK_TARGET = (
        ('_blank', _('Open in new window')),
        ('_self', _('Open in same window')),
        ('_parent', _('Delegate to parent')),
        ('_top', _('Delegate to top')),
    )

    # see cmsplugin_filer_image.models.FilerImage
    alt_text = models.CharField(
        _("alt text"), null=False, blank=False, max_length=255
    )

    width = models.PositiveIntegerField(_('width'), null=True, blank=True)

    height = models.PositiveIntegerField(_('height'), null=True, blank=True)

    # link models
    link_url = models.URLField(
        verbose_name=_('External URL'),
        blank=True,
        max_length=2040,
    )

    link_page = PageField(
        verbose_name=_('Internal URL'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    link_mailto = models.EmailField(
        verbose_name=_('Email address'),
        blank=True,
        max_length=255,
    )

    link_phone = models.CharField(
        verbose_name=_('Phone'),
        blank=True,
        max_length=255,
    )

    link_target = models.CharField(
        verbose_name=_('Link target'),
        choices=LINK_TARGET,
        blank=True,
        max_length=255,
    )

    link_attributes = AttributesField(
        verbose_name=_('Link attributes'),
        blank=True,
        excluded_keys=['href', 'target'],
    )

    def get_link(self):
        if self.link_page_id:
            return self.link_page.get_absolute_url(language=self.language)
        if self.link_url:
            return self.link_url
        if self.link_mailto:
            return 'mailto:%(address)s' % {
                'address': self.link_mailto,
            }
        if self.link_phone:
            return 'tel:%(number)s' % {
                'number': self.link_phone,
            }
        return False

    def __str__(self):
        return self.alt_text

    class Meta:
        verbose_name = _('SVG image')
        verbose_name_plural = _('SVG images')
