from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from django.utils.translation import ugettext_lazy as _

from .models import FilerSvgImagePluginModel, FilerSvgInlinePluginModel


class FilerSvgInlinePlugin(CMSPluginBase):
    model = FilerSvgInlinePluginModel
    name = _("Inline SVG image")
    module = 'Filer'
    render_template = 'ripiu/cmsplugin_filer_svg/inline.svg'
    allow_children = False


plugin_pool.register_plugin(FilerSvgInlinePlugin)


class FilerSvgImagePlugin(CMSPluginBase):
    model = FilerSvgImagePluginModel
    name = _("SVG image")
    module = 'Filer'
    render_template = 'ripiu/cmsplugin_filer_svg/ref.html'
    allow_children = False
    fieldsets = [
        (None, {
            'fields': (
                'file',
                'alt_text',
                ('width', 'height',),
            )
        }),
        (_('Link settings'), {
            'classes': ('collapse',),
            'fields': (
                ('link_page', 'link_url'),
                ('link_mailto', 'link_phone',),
                'link_target',
                'link_attributes',
            )
        }),
    ]

    def render(self, context, instance, placeholder):
        # assign link to a context variable to be performant
        context['picture_link'] = instance.get_link()
        return super().render(context, instance, placeholder)


plugin_pool.register_plugin(FilerSvgImagePlugin)
