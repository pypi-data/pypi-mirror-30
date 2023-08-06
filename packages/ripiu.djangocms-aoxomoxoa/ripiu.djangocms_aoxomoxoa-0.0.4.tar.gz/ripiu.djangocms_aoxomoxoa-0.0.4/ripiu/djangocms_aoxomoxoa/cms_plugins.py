import logging

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from django.conf import settings
from django.contrib import admin
from django.utils.html import mark_safe
from django.forms.models import model_to_dict
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.utils import flatten_fieldsets

from .admin import (
    SliderUniteOptionsAdmin, CarouselUniteOptionsAdmin,
    GridThemeUniteOptionsAdmin, TilesGridUniteOptionsAdmin,
    TilesNestedUniteOptionsAdmin, CompactThemeUniteOptionsAdmin,
    DefaultThemeUniteOptionsAdmin, TilesColumnsUniteOptionsAdmin,
    TilesJustifiedUniteOptionsAdmin,
)
from .models import plugins

logger = logging.getLogger(__name__)


class BaseUnitePluginPublisher(CMSPluginBase):
    fieldsets = (
        (_(''), {
            'fields': (
                'slug',
                'thumbnail_thumbnail_option',
                'full_thumbnail_option',
                'saved_conf',
                'attributes',
            ),
        }),
    )
    module = module = settings.RIPIU_AOXOMOXOA_MODULE_NAME
    allow_children = True
    render_template = 'ripiu/djangocms_aoxomoxoa/unite.html'
    admin_class = admin.ModelAdmin
    gallery_theme = None
    additional_options = {}
    theme_needs_stylesheet = False

    def __init__(self, model=None, admin_site=None):
        super().__init__(model, admin_site)
        if hasattr(self.admin_class, 'fieldsets') and\
           self.admin_class.fieldsets:
            self.fieldsets = self.fieldsets + self.admin_class.fieldsets

    def copy_relations(self, oldinstance):
        logger.debug("asdrubala")
        self.full_thumbnail_option = oldinstance.full_thumbnail_option
        self.thumbnail_thumbnail_option = oldinstance\
            .thumbnail_thumbnail_option
        self.saved_conf = oldinstance.saved_conf

    def render(self, context, instance, placeholder):
        import json
        context = super().render(context, instance, placeholder)
        classes = 'ripiu-unite '
        classes += instance.attributes.get('class', '')
        instance.attributes['class'] = classes
        fields = flatten_fieldsets(self.admin_class.fieldsets)
        active_conf = instance.saved_conf or instance
        conf = {
            k: v
            for (k, v) in model_to_dict(active_conf).items()
            if k in fields
            if v != instance._meta.get_field(k).default
        }
        if self.gallery_theme:
            conf.update({
                'gallery_theme': self.gallery_theme,
            })
            context.update({
                'gallery_theme': self.gallery_theme,
                'theme_needs_stylesheet': self.theme_needs_stylesheet
            })
        conf.update(self.additional_options)
        context.update({
            'unite_conf': mark_safe(json.dumps(conf)),
            'needs_jquery': settings.RIPIU_AOXOMOXOA_NEEDS_JQUERY,
            'thumbnail_size': instance.thumbnail_thumbnail_option,
            'full_size': instance.full_thumbnail_option,
        })
        return context


@plugin_pool.register_plugin
class CarouselPluginPublisher(BaseUnitePluginPublisher):
    model = plugins.CarouselPlugin
    name = _('Carousel')
    admin_class = CarouselUniteOptionsAdmin
    gallery_theme = 'carousel'


@plugin_pool.register_plugin
class CompactThemePluginPublisher(BaseUnitePluginPublisher):
    model = plugins.CompactThemePlugin
    name = _('Compact theme')
    admin_class = CompactThemeUniteOptionsAdmin
    gallery_theme = 'compact'


@plugin_pool.register_plugin
class DefaultThemePluginPublisher(BaseUnitePluginPublisher):
    model = plugins.DefaultThemePlugin
    name = _('Default theme')
    admin_class = DefaultThemeUniteOptionsAdmin
    gallery_theme = 'default'
    theme_needs_stylesheet = True


@plugin_pool.register_plugin
class GridThemePluginPublisher(BaseUnitePluginPublisher):
    model = plugins.GridThemePlugin
    name = _('Grid theme')
    admin_class = GridThemeUniteOptionsAdmin
    gallery_theme = 'grid'


@plugin_pool.register_plugin
class SliderPluginPublisher(BaseUnitePluginPublisher):
    model = plugins.SliderPlugin
    name = _('Slider')
    admin_class = SliderUniteOptionsAdmin
    gallery_theme = 'slider'


@plugin_pool.register_plugin
class TilesColumnsPluginPublisher(BaseUnitePluginPublisher):
    model = plugins.TilesColumnsPlugin
    name = _('Tiles - Columns')
    admin_class = TilesColumnsUniteOptionsAdmin
    gallery_theme = 'tiles'


@plugin_pool.register_plugin
class TilesGridPluginPublisher(BaseUnitePluginPublisher):
    model = plugins.TilesGridPlugin
    name = _('Tiles - Grid')
    admin_class = TilesGridUniteOptionsAdmin
    gallery_theme = 'tilesgrid'


@plugin_pool.register_plugin
class TilesJustifiedPluginPublisher(BaseUnitePluginPublisher):
    model = plugins.TilesJustifiedPlugin
    name = _('Tiles - Justified')
    admin_class = TilesJustifiedUniteOptionsAdmin
    gallery_theme = 'tiles'
    additional_options = {
        'tiles_type': 'justified',
    }


@plugin_pool.register_plugin
class TilesNestedPluginPublisher(BaseUnitePluginPublisher):
    model = plugins.TilesNestedPlugin
    name = _('Tiles - Nested')
    admin_class = TilesNestedUniteOptionsAdmin
    gallery_theme = ''
    additional_options = {
        'tiles_type': 'nested',
    }
