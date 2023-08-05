from cms.models import CMSPlugin
from djangocms_attributes_field.fields import AttributesField

from django.db import models
from django.utils.translation import ugettext_lazy as _

from .options import (
    SliderUniteOptions, CarouselUniteOptions, GridThemeUniteOptions,
    TilesGridUniteOptions, SliderSavedUniteOptions, TilesNestedUniteOptions,
    CompactThemeUniteOptions, DefaultThemeUniteOptions,
    TilesColumnsUniteOptions, CarouselSavedUniteOptions,
    GridThemeSavedUniteOptions, TilesGridSavedUniteOptions,
    TilesJustifiedUniteOptions, TilesNestedSavedUniteOptions,
    CompactThemeSavedUniteOptions, DefaultThemeSavedUniteOptions,
    TilesColumnsSavedUniteOptions, TilesJustifiedSavedUniteOptions,
)


class UnitePlugin(CMSPlugin):
    '''
    Base class for CMS plugins
    '''

    slug = models.SlugField(
        _('slug'), max_length=50
    )

    attributes = AttributesField(
        verbose_name=_('Attributes'),
        blank=True,
        excluded_keys=['id', 'style'],
    )

    def __str__(self):
        return str(self.slug)

    class Meta:
        abstract = True


class CarouselPlugin(CarouselUniteOptions, UnitePlugin):
    '''
    Carousel CMS plugin
    '''

    saved_conf = models.ForeignKey(
        CarouselSavedUniteOptions,
        related_name='instances',
        related_query_name='instance',
        blank=True, null=True,
        verbose_name=_('saved configuration'),
        help_text=_('Override the unite options with the values from the '
                     'selected saved configuration.')
    )

    thumbnail_thumbnail_option = models.ForeignKey(
        'filer.ThumbnailOption', null=False, blank=False,
        verbose_name=_('thumbnail thumbnail option'),
        related_name='carousel_unite_plugins_thumbnail',
        related_query_name='carousel_unite_plugin_thumbnail',
        # help_text=_('Small picture thumbnail option.')
    )

    full_thumbnail_option = models.ForeignKey(
        'filer.ThumbnailOption', null=False, blank=False,
        verbose_name=_('fullscreen thumbnail option'),
        related_name='carousel_unite_plugins_full',
        related_query_name='carousel_unite_plugin_full',
        # help_text=_('Big picture thumbnail option.')
    )

    class Meta:
        verbose_name = _('Carousel plugin')
        verbose_name_plural = _('Carousel plugins')


class CompactThemePlugin(CompactThemeUniteOptions, UnitePlugin):
    '''
    Compact theme CMS plugin
    '''

    saved_conf = models.ForeignKey(
        CompactThemeSavedUniteOptions,
        related_name='instances',
        related_query_name='instance',
        blank=True, null=True,
        verbose_name=_('saved configuration'),
        help_text=_('Override the unite options with the values from the '
                     'selected saved configuration.')
    )

    thumbnail_thumbnail_option = models.ForeignKey(
        'filer.ThumbnailOption', null=False, blank=False,
        verbose_name=_('thumbnail thumbnail option'),
        related_name='compacttheme_unite_plugins_thumbnail',
        related_query_name='compacttheme_unite_plugin_thumbnail',
        # help_text=_('Small picture thumbnail option.')
    )

    full_thumbnail_option = models.ForeignKey(
        'filer.ThumbnailOption', null=False, blank=False,
        verbose_name=_('fullscreen thumbnail option'),
        related_name='compacttheme_unite_plugins_full',
        related_query_name='compacttheme_unite_plugin_full',
        # help_text=_('Big picture thumbnail option.')
    )

    class Meta:
        verbose_name = _('Compact theme plugin')
        verbose_name_plural = _('Compact theme plugins')


class DefaultThemePlugin(DefaultThemeUniteOptions, UnitePlugin):
    '''
    Default theme CMS plugin
    '''

    saved_conf = models.ForeignKey(
        DefaultThemeSavedUniteOptions,
        related_name='instances',
        related_query_name='instance',
        blank=True, null=True,
        verbose_name=_('saved configuration'),
        help_text=_('Override the unite options with the values from the '
                     'selected saved configuration.')
    )

    thumbnail_thumbnail_option = models.ForeignKey(
        'filer.ThumbnailOption', null=False, blank=False,
        verbose_name=_('thumbnail thumbnail option'),
        related_name='defaulttheme_unite_plugins_thumbnail',
        related_query_name='defaulttheme_unite_plugin_thumbnail',
        # help_text=_('Small picture thumbnail option.')
    )

    full_thumbnail_option = models.ForeignKey(
        'filer.ThumbnailOption', null=False, blank=False,
        verbose_name=_('fullscreen thumbnail option'),
        related_name='defaulttheme_unite_plugins_full',
        related_query_name='defaulttheme_unite_plugin_full',
        # help_text=_('Big picture thumbnail option.')
    )

    class Meta:
        verbose_name = _('Default theme plugin')
        verbose_name_plural = _('Default theme plugins')


class GridThemePlugin(GridThemeUniteOptions, UnitePlugin):
    '''
    Grid theme CMS plugin
    '''

    saved_conf = models.ForeignKey(
        GridThemeSavedUniteOptions,
        related_name='instances',
        related_query_name='instance',
        blank=True, null=True,
        verbose_name=_('saved configuration'),
        help_text=_('Override the unite options with the values from the '
                     'selected saved configuration.')
    )

    thumbnail_thumbnail_option = models.ForeignKey(
        'filer.ThumbnailOption', null=False, blank=False,
        verbose_name=_('thumbnail thumbnail option'),
        related_name='gridtheme_unite_plugins_thumbnail',
        related_query_name='gridtheme_unite_plugin_thumbnail',
        # help_text=_('Small picture thumbnail option.')
    )

    full_thumbnail_option = models.ForeignKey(
        'filer.ThumbnailOption', null=False, blank=False,
        verbose_name=_('fullscreen thumbnail option'),
        related_name='gridtheme_unite_plugins_full',
        related_query_name='gridtheme_unite_plugin_full',
        # help_text=_('Big picture thumbnail option.')
    )

    class Meta:
        verbose_name = _('Grid theme plugin')
        verbose_name_plural = _('Grid theme plugins')


class SliderPlugin(SliderUniteOptions, UnitePlugin):
    '''
    Slider CMS plugin
    '''

    saved_conf = models.ForeignKey(
        SliderSavedUniteOptions,
        related_name='instances',
        related_query_name='instance',
        blank=True, null=True,
        verbose_name=_('saved configuration'),
        help_text=_('Override the unite options with the values from the '
                     'selected saved configuration.')
    )

    thumbnail_thumbnail_option = models.ForeignKey(
        'filer.ThumbnailOption', null=False, blank=False,
        verbose_name=_('thumbnail thumbnail option'),
        related_name='slider_unite_plugins_thumbnail',
        related_query_name='slider_unite_plugin_thumbnail',
        # help_text=_('Small picture thumbnail option.')
    )

    full_thumbnail_option = models.ForeignKey(
        'filer.ThumbnailOption', null=False, blank=False,
        verbose_name=_('fullscreen thumbnail option'),
        related_name='slider_unite_plugins_full',
        related_query_name='slider_unite_plugin_full',
        # help_text=_('Big picture thumbnail option.')
    )

    class Meta:
        verbose_name = _('Slider plugin')
        verbose_name_plural = _('Slider plugins')


class TilesColumnsPlugin(TilesColumnsUniteOptions, UnitePlugin):
    '''
    Tiles - Columns CMS plugin
    '''

    saved_conf = models.ForeignKey(
        TilesColumnsSavedUniteOptions,
        related_name='instances',
        related_query_name='instance',
        blank=True, null=True,
        verbose_name=_('saved configuration'),
        help_text=_('Override the unite options with the values from the '
                     'selected saved configuration.')
    )

    thumbnail_thumbnail_option = models.ForeignKey(
        'filer.ThumbnailOption', null=False, blank=False,
        verbose_name=_('thumbnail thumbnail option'),
        related_name='tilescolumns_unite_plugins_thumbnail',
        related_query_name='tilescolumns_unite_plugin_thumbnail',
        # help_text=_('Small picture thumbnail option.')
    )

    full_thumbnail_option = models.ForeignKey(
        'filer.ThumbnailOption', null=False, blank=False,
        verbose_name=_('fullscreen thumbnail option'),
        related_name='tilescolumns_unite_plugins_full',
        related_query_name='tilescolumns_unite_plugin_full',
        # help_text=_('Big picture thumbnail option.')
    )

    class Meta:
        verbose_name = _('Tiles - Columns plugin')
        verbose_name_plural = _('Tiles - Columns plugins')


class TilesGridPlugin(TilesGridUniteOptions, UnitePlugin):
    '''
    Tiles - Grid CMS plugin
    '''

    saved_conf = models.ForeignKey(
        TilesGridSavedUniteOptions,
        related_name='instances',
        related_query_name='instance',
        blank=True, null=True,
        verbose_name=_('saved configuration'),
        help_text=_('Override the unite options with the values from the '
                    'selected saved configuration.')
    )

    thumbnail_thumbnail_option = models.ForeignKey(
        'filer.ThumbnailOption', null=False, blank=False,
        verbose_name=_('thumbnail thumbnail option'),
        related_name='tilesgrid_unite_plugins_thumbnail',
        related_query_name='tilesgrid_unite_plugin_thumbnail',
        # help_text=_('Small picture thumbnail option.')
    )

    full_thumbnail_option = models.ForeignKey(
        'filer.ThumbnailOption', null=False, blank=False,
        verbose_name=_('fullscreen thumbnail option'),
        related_name='tilesgrid_unite_plugins_full',
        related_query_name='tilesgrid_unite_plugin_full',
        # help_text=_('Big picture thumbnail option.')
    )

    class Meta:
        verbose_name = _('Tiles - Grid plugin')
        verbose_name_plural = _('Tiles - Grid plugins')


class TilesJustifiedPlugin(TilesJustifiedUniteOptions, UnitePlugin):
    '''
    Tiles - Justified CMS plugin
    '''

    saved_conf = models.ForeignKey(
        TilesJustifiedSavedUniteOptions,
        related_name='instances',
        related_query_name='instance',
        blank=True, null=True,
        verbose_name=_('saved configuration'),
        help_text=_('Override the unite options with the values from the '
                    'selected saved configuration.')
    )

    thumbnail_thumbnail_option = models.ForeignKey(
        'filer.ThumbnailOption', null=False, blank=False,
        verbose_name=_('thumbnail thumbnail option'),
        related_name='tilesjustified_unite_plugins_thumbnail',
        related_query_name='tilesjustified_unite_plugin_thumbnail',
        # help_text=_('Small picture thumbnail option.')
    )

    full_thumbnail_option = models.ForeignKey(
        'filer.ThumbnailOption', null=False, blank=False,
        verbose_name=_('fullscreen thumbnail option'),
        related_name='tilesjustified_unite_plugins_full',
        related_query_name='tilesjustified_unite_plugin_full',
        # help_text=_('Big picture thumbnail option.')
    )

    class Meta:
        verbose_name = _('Tiles - Justified plugin')
        verbose_name_plural = _('Tiles - Justified plugins')


class TilesNestedPlugin(TilesNestedUniteOptions, UnitePlugin):
    '''
    Tiles - Nested CMS plugin
    '''

    saved_conf = models.ForeignKey(
        TilesNestedSavedUniteOptions,
        related_name='instances',
        related_query_name='instance',
        blank=True, null=True,
        verbose_name=_('saved configuration'),
        help_text=_('Override the unite options with the values from the '
                    'selected saved configuration.')
    )

    thumbnail_thumbnail_option = models.ForeignKey(
        'filer.ThumbnailOption', null=False, blank=False,
        verbose_name=_('thumbnail thumbnail option'),
        related_name='tilesnested_unite_plugins_thumbnail',
        related_query_name='tilesnested_unite_plugin_thumbnail',
        # help_text=_('Small picture thumbnail option.')
    )

    full_thumbnail_option = models.ForeignKey(
        'filer.ThumbnailOption', null=False, blank=False,
        verbose_name=_('fullscreen thumbnail option'),
        related_name='tilesnested_unite_plugins_full',
        related_query_name='tilesnested_unite_plugin_full',
        # help_text=_('Big picture thumbnail option.')
    )

    class Meta:
        verbose_name = _('Tiles - Nested plugin')
        verbose_name_plural = _('Tiles - Nested plugins')
